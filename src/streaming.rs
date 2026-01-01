use actix_web::web::Bytes;
use futures_util::future::join_all;
use futures_util::{stream, Stream};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes, PyMemoryView, PyString};
use std::pin::Pin;
use std::sync::atomic::Ordering;
use tokio::sync::mpsc;

use crate::state::{get_max_sync_streaming_threads, ACTIVE_SYNC_STREAMING_THREADS, TASK_LOCALS};
// Streaming uses direct_stream only in higher-level handler; not directly here

// Buffer pool imports removed (unused)

// Note: buffer pool removed during modularization; reintroduce if needed for micro-alloc tuning

// Reuse the global Python asyncio event loop created at server startup (TASK_LOCALS)

#[inline(always)]
pub fn convert_python_chunk(value: &Bound<'_, PyAny>) -> Option<Bytes> {
    if let Ok(py_bytes) = value.cast::<PyBytes>() {
        return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
    }
    if let Ok(py_bytearray) = value.cast::<PyByteArray>() {
        return Some(Bytes::copy_from_slice(unsafe { py_bytearray.as_bytes() }));
    }
    if let Ok(py_str) = value.cast::<PyString>() {
        if let Ok(s) = py_str.to_str() {
            return Some(Bytes::from(s.to_owned()));
        }
        let s = py_str.to_string_lossy().into_owned();
        return Some(Bytes::from(s.into_bytes()));
    }
    if let Ok(memory_view) = value.cast::<PyMemoryView>() {
        if let Ok(bytes_obj) = memory_view.call_method0("tobytes") {
            if let Ok(py_bytes) = bytes_obj.cast::<PyBytes>() {
                return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
            }
        }
    }
    if value.hasattr("__bytes__").unwrap_or(false) {
        if let Ok(buffer) = value.call_method0("__bytes__") {
            if let Ok(py_bytes) = buffer.cast::<PyBytes>() {
                return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
            }
        }
    }
    if let Ok(py_str) = value.str() {
        let s = py_str.to_string_lossy().into_owned();
        return Some(Bytes::from(s.into_bytes()));
    }
    None
}

/// Create a stream with default batch sizes from environment
pub fn create_python_stream(
    content: Py<PyAny>,
    is_async_generator: bool,
) -> Pin<Box<dyn Stream<Item = Result<Bytes, std::io::Error>> + Send>> {
    let batch_size: usize = std::env::var("DJANGO_BOLT_STREAM_BATCH_SIZE")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .unwrap_or(20);
    let sync_batch_size: usize = std::env::var("DJANGO_BOLT_STREAM_SYNC_BATCH_SIZE")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .unwrap_or(5);
    create_python_stream_with_config(content, batch_size, sync_batch_size, is_async_generator)
}

/// Create a stream for SSE that sends items immediately (batch_size=1)
pub fn create_sse_stream(
    content: Py<PyAny>,
    is_async_generator: bool,
) -> Pin<Box<dyn Stream<Item = Result<Bytes, std::io::Error>> + Send>> {
    create_python_stream_with_config(content, 1, 1, is_async_generator)
}

/// Internal function with configurable batch sizes
fn create_python_stream_with_config(
    content: Py<PyAny>,
    async_batch_size: usize,
    sync_batch_size: usize,
    is_async_from_metadata: bool,
) -> Pin<Box<dyn Stream<Item = Result<Bytes, std::io::Error>> + Send>> {
    let channel_capacity: usize = std::env::var("DJANGO_BOLT_STREAM_CHANNEL_CAPACITY")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .unwrap_or(32);
    let fast_path_threshold: usize = std::env::var("DJANGO_BOLT_STREAM_FAST_PATH_THRESHOLD")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .unwrap_or(10);
    // Note: content is guaranteed to be a generator instance (not a callable)
    // because StreamingResponse validates this in Python at instantiation time.
    // The is_async_generator flag was pre-computed from Python's inspect.
    let resolved_target = Python::attach(|py| content.clone_ref(py));
    let is_async_iter = is_async_from_metadata;


    let (tx, rx) = mpsc::channel::<Result<Bytes, std::io::Error>>(channel_capacity);
    let resolved_target_final = Python::attach(|py| resolved_target.clone_ref(py));
    let is_async_final = is_async_iter;

    if is_async_final {
        let fast_path = fast_path_threshold;
        tokio::spawn(async move {
            let is_optimized_batcher = Python::attach(|py| {
                if let Ok(name) = resolved_target_final.bind(py).get_type().name() {
                    name.to_string().contains("OptimizedStreamBatcher")
                } else {
                    false
                }
            });

            let async_iter: Option<Py<PyAny>> = Python::attach(|py| {
                let b = resolved_target_final.bind(py);
                if b.hasattr("__aiter__").unwrap_or(false) {
                    match b.call_method0("__aiter__") {
                        Ok(it) => Some(it.unbind()),
                        Err(_) => None,
                    }
                } else if b.hasattr("__anext__").unwrap_or(false) {
                    Some(resolved_target_final.clone_ref(py))
                } else {
                    None
                }
            });


            if async_iter.is_none() {
                let _ = tx
                    .send(Err(std::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        "Failed to initialize async iterator",
                    )))
                    .await;
                return;
            }
            let async_iter = async_iter.unwrap();

            let mut exhausted = false;
            let mut batch_futures = Vec::with_capacity(async_batch_size);
            let mut consecutive_small_batches = 0u8;
            let mut current_batch_size = std::cmp::min(async_batch_size, fast_path);

            while !exhausted {
                batch_futures.clear();
                Python::attach(|py| {
                    // Reuse the global event loop locals initialized at server startup
                    let locals = match TASK_LOCALS.get() {
                        Some(l) => l,
                        None => {
                            exhausted = true;
                            return;
                        }
                    };

                    let iterations = if is_optimized_batcher {
                        1
                    } else {
                        current_batch_size
                    };
                    for _ in 0..iterations {
                        match async_iter.bind(py).call_method0("__anext__") {
                            Ok(awaitable) => {
                                match pyo3_async_runtimes::into_future_with_locals(
                                    locals, awaitable,
                                ) {
                                    Ok(f) => batch_futures.push(f),
                                    Err(_) => {
                                        exhausted = true;
                                        break;
                                    }
                                }
                            }
                            Err(e) => {
                                if e.is_instance_of::<pyo3::exceptions::PyStopAsyncIteration>(py) {
                                    exhausted = true;
                                }
                                break;
                            }
                        }
                    }
                });


                if batch_futures.len() < current_batch_size / 2 {
                    consecutive_small_batches += 1;
                    if consecutive_small_batches >= 3 && current_batch_size > 1 {
                        current_batch_size = std::cmp::max(1, current_batch_size / 2);
                        consecutive_small_batches = 0;
                    }
                } else if batch_futures.len() == current_batch_size
                    && current_batch_size < async_batch_size
                {
                    current_batch_size = std::cmp::min(async_batch_size, current_batch_size * 2);
                    consecutive_small_batches = 0;
                }

                if batch_futures.is_empty() {
                    break;
                }

                let results = join_all(batch_futures.drain(..)).await;

                let mut got_stop_iteration = false;
                for result in results {
                    match result {
                        Ok(obj) => {
                            let bytes_opt = Python::attach(|py| {
                                let v = obj.bind(py);
                                if is_optimized_batcher {
                                    if let Ok(py_bytes) = v.cast::<PyBytes>() {
                                        Some(Bytes::copy_from_slice(py_bytes.as_bytes()))
                                    } else {
                                        super::streaming::convert_python_chunk(&v)
                                    }
                                } else {
                                    super::streaming::convert_python_chunk(&v)
                                }
                            });
                            if let Some(bytes) = bytes_opt {
                                if tx.send(Ok(bytes)).await.is_err() {
                                    // Client disconnected - close the async generator to run cleanup code
                                    let close_result = Python::attach(|py| {
                                        let iter_bound = async_iter.bind(py);
                                        if iter_bound.hasattr("aclose").unwrap_or(false) {
                                            if let Ok(awaitable) = iter_bound.call_method0("aclose") {
                                                if let Some(locals) = TASK_LOCALS.get() {
                                                    return pyo3_async_runtimes::into_future_with_locals(locals, awaitable).ok();
                                                } else {
                                                    eprintln!("[SSE WARNING] Unable to get task locals for async generator cleanup on disconnect");
                                                }
                                            } else {
                                                eprintln!("[SSE WARNING] Failed to call aclose() on async generator during disconnect cleanup");
                                            }
                                        }
                                        None
                                    });
                                    // Await the cleanup if we got a future
                                    if let Some(close_future) = close_result {
                                        if let Err(e) = close_future.await {
                                            eprintln!("[SSE WARNING] Error during async generator cleanup on client disconnect: {}", e);
                                        }
                                    }
                                    exhausted = true;
                                    break;
                                }
                            }
                        }
                        Err(e) => {
                            Python::attach(|py| {
                                if e.is_instance_of::<pyo3::exceptions::PyStopAsyncIteration>(py) {
                                    got_stop_iteration = true;
                                    exhausted = true;
                                }
                            });
                        }
                    }
                }
                if got_stop_iteration {
                    exhausted = true;
                }
            }

            // Ensure async generator cleanup runs
            let close_result = Python::attach(|py| {
                let iter_bound = async_iter.bind(py);
                if iter_bound.hasattr("aclose").unwrap_or(false) {
                    if let Ok(awaitable) = iter_bound.call_method0("aclose") {
                        if let Some(locals) = TASK_LOCALS.get() {
                            return pyo3_async_runtimes::into_future_with_locals(locals, awaitable).ok();
                        } else {
                            eprintln!("[SSE WARNING] Unable to get task locals for async generator cleanup at end of stream");
                        }
                    } else {
                        eprintln!("[SSE WARNING] Failed to call aclose() on async generator at end of stream cleanup");
                    }
                }
                None
            });
            if let Some(close_future) = close_result {
                if let Err(e) = close_future.await {
                    eprintln!("[SSE WARNING] Error during async generator cleanup at end of stream: {}", e);
                }
            }

        });

        // Async streaming successful, return stream
        let s = stream::unfold(rx, |mut rx| async move {
            match rx.recv().await {
                Some(item) => Some((item, rx)),
                None => None,
            }
        });
        return Box::pin(s);
    } else {
        let sync_batch = sync_batch_size;

        // OPTION 3: Use std::thread::spawn() instead of spawn_blocking()
        // This avoids Tokio's blocking thread pool limit entirely
        // Each sync SSE connection runs on its own dedicated OS thread

        // Make tx cloneable for the spawn failure case
        let tx_for_spawn = tx.clone();

        // Check connection limits to prevent thread exhaustion DoS
        let max_threads = get_max_sync_streaming_threads();
        let current_threads = ACTIVE_SYNC_STREAMING_THREADS.load(Ordering::Relaxed);

        if current_threads >= max_threads {
            eprintln!("[SSE WARNING] Sync streaming thread limit reached: {} >= {}", current_threads, max_threads);
            // Spawn async task to send retry directive (can't use blocking_send from runtime)
            tokio::spawn({
                let tx_clone = tx.clone();
                async move {
                    // RFC 6553 Server-Sent Events: send retry directive before closing
                    let retry_directive = b"retry: 30000\n\n";
                    let _ = tx_clone.send(Ok(Bytes::from_static(retry_directive))).await;
                }
            });
            drop(tx);
            let s = stream::unfold(rx, |mut rx| async move {
                match rx.recv().await {
                    Some(item) => Some((item, rx)),
                    None => None,
                }
            });
            return Box::pin(s);
        }

        // Increment active thread counter
        ACTIVE_SYNC_STREAMING_THREADS.fetch_add(1, Ordering::Relaxed);

        // Use Builder::new() to get a Result on thread spawn failure
        match std::thread::Builder::new()
            .name("sync-sse-generator".to_string())
            .spawn(move || {
            let mut iterator: Option<Py<PyAny>> = None;
            let mut batch_buffer = Vec::with_capacity(sync_batch);
            let mut exhausted = false;

            loop {
                batch_buffer.clear();
                let python_exhausted = Python::attach(|py| {
                    if iterator.is_none() {
                        let iter_target = resolved_target_final.clone_ref(py);
                        let bound = iter_target.bind(py);
                        let iter_obj = if bound.hasattr("__next__").unwrap_or(false) {
                            iter_target
                        } else if bound.hasattr("__iter__").unwrap_or(false) {
                            match bound.call_method0("__iter__") {
                                Ok(it) => it.unbind(),
                                Err(_) => return true,
                            }
                        } else {
                            return true;
                        };
                        iterator = Some(iter_obj);
                    }
                    let it = iterator.as_ref().unwrap().bind(py);
                    for _ in 0..sync_batch {
                        match it.call_method0("__next__") {
                            Ok(value) => {
                                if let Some(bytes) = super::streaming::convert_python_chunk(&value)
                                {
                                    batch_buffer.push(bytes);
                                }
                            }
                            Err(err) => {
                                if err.is_instance_of::<pyo3::exceptions::PyStopIteration>(py) {
                                    return true;
                                }
                                break;
                            }
                        }
                    }
                    false
                });
                if python_exhausted {
                    exhausted = true;
                }
                if batch_buffer.is_empty() && exhausted {
                    break;
                }
                for bytes in batch_buffer.drain(..) {
                    // Use blocking_send which works from non-async context
                    if tx.blocking_send(Ok(bytes)).is_err() {
                        // Client disconnected - close the generator to run cleanup code
                        if let Some(ref iter) = iterator {
                            Python::attach(|py| {
                                match iter.bind(py).call_method0("close") {
                                    Ok(_) => {},
                                    Err(e) => {
                                        eprintln!("[SSE WARNING] Error during sync generator cleanup on client disconnect: {}", e);
                                    }
                                }
                            });
                        }
                        exhausted = true;
                        break;
                    }
                }
                if exhausted {
                    break;
                }
            }

            // Ensure sync generator cleanup runs
            if let Some(ref iter) = iterator {
                Python::attach(|py| {
                    match iter.bind(py).call_method0("close") {
                        Ok(_) => {},
                        Err(e) => {
                            eprintln!("[SSE WARNING] Error during sync generator cleanup at end of stream: {}", e);
                        }
                    }
                });
            }
            // Decrement thread counter when thread finishes
            ACTIVE_SYNC_STREAMING_THREADS.fetch_sub(1, Ordering::Relaxed);
        }) {
            Ok(_) => {
                // Thread spawned successfully, SSE will start streaming
            }
            Err(e) => {
                eprintln!("[SSE ERROR] Failed to spawn sync streaming thread: {}", e);
                // Decrement counter since thread spawn failed
                ACTIVE_SYNC_STREAMING_THREADS.fetch_sub(1, Ordering::Relaxed);
                // Spawn async task to send retry directive (can't use blocking_send from runtime)
                tokio::spawn({
                    let tx_clone = tx_for_spawn.clone();
                    async move {
                        // RFC 6553 Server-Sent Events: send retry directive before closing
                        let retry_directive = b"retry: 30000\n\n";
                        let _ = tx_clone.send(Ok(Bytes::from_static(retry_directive))).await;
                    }
                });
                drop(tx_for_spawn);
            }
        }

        // Create simple stream without error state in closure (keeps Stream trait bounds clean)
        let s = stream::unfold(rx, |mut rx| async move {
            match rx.recv().await {
                Some(item) => Some((item, rx)),
                None => None,
            }
        });
        Box::pin(s)
    }
}
