use actix_web::web::Bytes;
use futures_util::{stream, Stream};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes, PyMemoryView, PyString};
use std::pin::Pin;
use std::time::Instant;
use tokio::sync::mpsc;

use crate::state::TASK_LOCALS;
// Streaming uses direct_stream only in higher-level handler; not directly here

// Buffer pool imports removed (unused)

// Note: buffer pool removed during modularization; reintroduce if needed for micro-alloc tuning

#[inline(always)]
pub fn convert_python_chunk(value: &Bound<'_, PyAny>) -> Option<Bytes> {
    if let Ok(py_bytes) = value.downcast::<PyBytes>() {
        return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
    }
    if let Ok(py_bytearray) = value.downcast::<PyByteArray>() {
        return Some(Bytes::copy_from_slice(unsafe { py_bytearray.as_bytes() }));
    }
    if let Ok(py_str) = value.downcast::<PyString>() {
        if let Ok(s) = py_str.to_str() {
            return Some(Bytes::from(s.to_owned()));
        }
        let s = py_str.to_string_lossy().into_owned();
        return Some(Bytes::from(s.into_bytes()));
    }
    if let Ok(memory_view) = value.downcast::<PyMemoryView>() {
        if let Ok(bytes_obj) = memory_view.call_method0("tobytes") {
            if let Ok(py_bytes) = bytes_obj.downcast::<PyBytes>() {
                return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
            }
        }
    }
    if value.hasattr("__bytes__").unwrap_or(false) {
        if let Ok(buffer) = value.call_method0("__bytes__") {
            if let Ok(py_bytes) = buffer.downcast::<PyBytes>() {
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

pub fn create_python_stream(
    content: Py<PyAny>,
) -> Pin<Box<dyn Stream<Item = Result<Bytes, std::io::Error>> + Send>> {
    let debug_timing = std::env::var("DJANGO_BOLT_DEBUG_TIMING").is_ok();

    let channel_capacity: usize = std::env::var("DJANGO_BOLT_STREAM_CHANNEL_CAPACITY")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .unwrap_or(32);
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
    let fast_path_threshold: usize = std::env::var("DJANGO_BOLT_STREAM_FAST_PATH_THRESHOLD")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .unwrap_or(10);

    let resolve_start = if debug_timing {
        Some(Instant::now())
    } else {
        None
    };
    let (resolved_target, is_async_iter) = Python::attach(|py| {
        let mut target = content.clone_ref(py);
        let obj = content.bind(py);
        if obj.is_callable() {
            if let Ok(new_obj) = obj.call0() {
                target = new_obj.unbind();
            }
        }
        let b = target.bind(py);
        let has_async =
            b.hasattr("__aiter__").unwrap_or(false) || b.hasattr("__anext__").unwrap_or(false);
        (target, has_async)
    });

    if let Some(start) = resolve_start {
        eprintln!(
            "[TIMING] Iterator resolution: {:?}, is_async={}, batch_size={}, fast_path_threshold={}",
            start.elapsed(),
            is_async_iter,
            if is_async_iter { batch_size } else { sync_batch_size },
            fast_path_threshold
        );
    }

    let (tx, rx) = mpsc::channel::<Result<Bytes, std::io::Error>>(channel_capacity);
    let resolved_target_final = Python::attach(|py| resolved_target.clone_ref(py));
    let is_async_final = is_async_iter;

    if is_async_final {
        let debug_async = debug_timing;
        let async_batch_size = batch_size;
        let fast_path = fast_path_threshold;
        tokio::spawn(async move {
            use futures_util::future::join_all;
            let mut chunk_count = 0u32;
            let mut total_gil_time = std::time::Duration::ZERO;
            let mut total_await_time = std::time::Duration::ZERO;
            let mut total_send_time = std::time::Duration::ZERO;
            let task_start = if debug_async {
                Some(Instant::now())
            } else {
                None
            };
            let init_start = if debug_async {
                Some(Instant::now())
            } else {
                None
            };

            let is_optimized_batcher = Python::attach(|py| {
                if let Ok(name) = resolved_target_final.bind(py).get_type().name() {
                    name.to_string().contains("OptimizedStreamBatcher")
                } else {
                    false
                }
            });

            let async_iter: Option<Py<PyAny>> = Python::attach(|py| {
                let b = resolved_target_final.bind(py);
                if debug_async {
                    eprintln!(
                        "[DEBUG] Checking async iterator: has __aiter__={}, has __anext__={}, is_optimized={}",
                        b.hasattr("__aiter__").unwrap_or(false),
                        b.hasattr("__anext__").unwrap_or(false),
                        is_optimized_batcher
                    );
                }
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

            if let Some(start) = init_start {
                eprintln!(
                    "[TIMING] Async iterator initialization: {:?}",
                    start.elapsed()
                );
            }

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
            let mut batch_count = 0usize;
            let mut consecutive_small_batches = 0u8;
            let mut current_batch_size = std::cmp::min(async_batch_size, fast_path);

            while !exhausted {
                let batch_start = if debug_async {
                    Some(Instant::now())
                } else {
                    None
                };
                batch_futures.clear();
                Python::attach(|py| {
                    let locals_owned;
                    let locals = if let Some(globals) = TASK_LOCALS.get() {
                        globals
                    } else {
                        match pyo3_async_runtimes::tokio::get_current_locals(py) {
                            Ok(l) => {
                                locals_owned = l;
                                &locals_owned
                            }
                            Err(_) => {
                                exhausted = true;
                                return;
                            }
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
                                    &locals, awaitable,
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

                if let Some(start) = batch_start {
                    eprintln!(
                        "[TIMING] Batch {} future collection ({} futures, target={}): {:?}",
                        batch_count,
                        batch_futures.len(),
                        current_batch_size,
                        start.elapsed()
                    );
                }

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

                let await_start = if debug_async {
                    Some(Instant::now())
                } else {
                    None
                };
                let results = join_all(batch_futures.drain(..)).await;
                if let Some(start) = await_start {
                    eprintln!(
                        "[TIMING] Batch {} await ({} futures): {:?}",
                        batch_count,
                        results.len(),
                        start.elapsed()
                    );
                    total_await_time += start.elapsed();
                }

                let convert_start = if debug_async {
                    Some(Instant::now())
                } else {
                    None
                };
                let mut send_count = 0;
                let mut got_stop_iteration = false;
                for result in results {
                    match result {
                        Ok(obj) => {
                            let bytes_opt = Python::attach(|py| {
                                let v = obj.bind(py);
                                if is_optimized_batcher {
                                    if let Ok(py_bytes) = v.downcast::<PyBytes>() {
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
                                    exhausted = true;
                                    break;
                                }
                                send_count += 1;
                                chunk_count += 1;
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
                if let Some(start) = convert_start {
                    eprintln!(
                        "[TIMING] Batch {} convert & send ({} chunks): {:?}",
                        batch_count,
                        send_count,
                        start.elapsed()
                    );
                    let elapsed = start.elapsed();
                    total_gil_time += elapsed;
                    total_send_time += elapsed;
                }
                batch_count += 1;
            }

            if let Some(start) = task_start {
                let total = start.elapsed();
                eprintln!("[TIMING] Async streaming complete (OPTIMIZED):");
                eprintln!("  Total time: {:?}", total);
                eprintln!("  Chunks sent: {}", chunk_count);
                eprintln!("  Batches processed: {}", batch_count);
                eprintln!("  Await time: {:?}", total_await_time);
                eprintln!("  Send time: {:?}", total_send_time);
                eprintln!("  GIL time: {:?}", total_gil_time);
            }
        });
    } else {
        let debug_sync = debug_timing;
        let sync_batch = sync_batch_size;
        tokio::task::spawn_blocking(move || {
            let mut iterator: Option<Py<PyAny>> = None;
            let mut chunk_count = 0u32;
            let mut batch_count = 0u32;
            let mut total_gil_time = std::time::Duration::ZERO;
            let mut total_send_time = std::time::Duration::ZERO;
            let task_start = if debug_sync {
                Some(Instant::now())
            } else {
                None
            };
            let mut batch_buffer = Vec::with_capacity(sync_batch);
            loop {
                let gil_start = if debug_sync {
                    Some(Instant::now())
                } else {
                    None
                };
                batch_buffer.clear();
                let exhausted = Python::attach(|py| {
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
                if let Some(start) = gil_start {
                    total_gil_time += start.elapsed();
                }
                if batch_buffer.is_empty() && exhausted {
                    break;
                }
                let send_start = if debug_sync {
                    Some(Instant::now())
                } else {
                    None
                };
                for bytes in batch_buffer.drain(..) {
                    if tx.blocking_send(Ok(bytes)).is_err() {
                        break;
                    }
                    chunk_count += 1;
                }
                if let Some(start) = send_start {
                    total_send_time += start.elapsed();
                }
                batch_count += 1;
                if exhausted {
                    break;
                }
            }
            if let Some(start) = task_start {
                let total = start.elapsed();
                eprintln!("[TIMING] Sync streaming complete (OPTIMIZED):");
                eprintln!("  Total time: {:?}", total);
                eprintln!("  Chunks sent: {}", chunk_count);
                eprintln!("  Batches processed: {}", batch_count);
                eprintln!("  GIL time: {:?}", total_gil_time);
                eprintln!("  Send time: {:?}", total_send_time);
            }
        });
    }

    let s = stream::unfold(rx, |mut rx| async move {
        match rx.recv().await {
            Some(item) => Some((item, rx)),
            None => None,
        }
    });
    Box::pin(s)
}
