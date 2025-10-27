use actix_web::web::Bytes;
use futures_util::Stream;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};
use std::pin::Pin;
use std::task::{Context, Poll};

/// Direct Python-to-HTTP streaming without channels or spawn_blocking
pub struct PythonDirectStream {
    iterator: Option<Py<PyAny>>,
    is_async: bool,
    exhausted: bool,
    // For small response optimization
    buffer: Vec<Bytes>,
    collected_size: usize,
    collect_threshold: usize,
}

impl PythonDirectStream {
    pub fn new(content: Py<PyAny>) -> Self {
        // Determine if we should collect or stream
        let collect_threshold = 8192; // 8KB threshold for SSE

        // Resolve iterator and check if async
        let (iterator, is_async) = Python::attach(|py| {
            let obj = content.bind(py);

            // If callable, call it to get iterator
            let target = if obj.is_callable() {
                match obj.call0() {
                    Ok(result) => result.unbind(),
                    Err(_) => content.clone_ref(py),
                }
            } else {
                content.clone_ref(py)
            };

            let bound = target.bind(py);
            let is_async = bound.hasattr("__aiter__").unwrap_or(false)
                || bound.hasattr("__anext__").unwrap_or(false);

            // For sync iterators, get the iterator object
            let iter = if !is_async {
                if bound.hasattr("__next__").unwrap_or(false) {
                    target
                } else if bound.hasattr("__iter__").unwrap_or(false) {
                    match bound.call_method0("__iter__") {
                        Ok(it) => it.unbind(),
                        Err(_) => target,
                    }
                } else {
                    target
                }
            } else {
                // For async, we'll handle it differently
                if bound.hasattr("__aiter__").unwrap_or(false) {
                    match bound.call_method0("__aiter__") {
                        Ok(it) => it.unbind(),
                        Err(_) => target,
                    }
                } else {
                    target
                }
            };

            (iter, is_async)
        });

        Self {
            iterator: Some(iterator),
            is_async,
            exhausted: false,
            buffer: Vec::with_capacity(32),
            collected_size: 0,
            collect_threshold,
        }
    }

    /// Try to collect small responses for optimization
    pub fn try_collect_small(&mut self) -> Option<Bytes> {
        if self.is_async || self.exhausted {
            return None;
        }

        let mut collected = Vec::new();
        let mut total_size = 0usize;

        Python::attach(|py| {
            if let Some(ref iter) = self.iterator {
                let bound = iter.bind(py);

                // Try to collect up to threshold
                while total_size < self.collect_threshold {
                    match bound.call_method0("__next__") {
                        Ok(value) => {
                            if let Some(bytes) = convert_to_bytes(&value) {
                                total_size += bytes.len();
                                collected.push(bytes);
                            }
                        }
                        Err(err) => {
                            if err.is_instance_of::<pyo3::exceptions::PyStopIteration>(py) {
                                self.exhausted = true;
                                break;
                            }
                            break;
                        }
                    }
                }
            }
        });

        if self.exhausted && total_size < self.collect_threshold {
            // Small response - return all as one
            let mut result = Vec::with_capacity(total_size);
            for chunk in collected {
                result.extend_from_slice(&chunk);
            }
            self.iterator = None; // Clean up
            Some(Bytes::from(result))
        } else {
            // Too large or not exhausted - save to buffer for streaming
            self.buffer = collected;
            self.collected_size = total_size;
            None
        }
    }
}

impl Stream for PythonDirectStream {
    type Item = Result<Bytes, std::io::Error>;

    fn poll_next(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        if self.exhausted && self.buffer.is_empty() {
            return Poll::Ready(None);
        }

        // Return buffered items first
        if !self.buffer.is_empty() {
            return Poll::Ready(Some(Ok(self.buffer.remove(0))));
        }

        if self.is_async {
            // Async iterators not supported in direct stream yet
            // This should have been handled by try_collect_small or fallback
            self.exhausted = true;
            return Poll::Ready(None);
        }

        // Sync iterator - get next chunk directly
        let next = Python::attach(|py| {
            if let Some(ref iter) = self.iterator {
                let bound = iter.bind(py);
                match bound.call_method0("__next__") {
                    Ok(value) => convert_to_bytes(&value),
                    Err(err) => {
                        if err.is_instance_of::<pyo3::exceptions::PyStopIteration>(py) {
                            self.exhausted = true;
                        }
                        None
                    }
                }
            } else {
                None
            }
        });

        match next {
            Some(bytes) => Poll::Ready(Some(Ok(bytes))),
            None => {
                if self.exhausted {
                    self.iterator = None; // Clean up
                    Poll::Ready(None)
                } else {
                    Poll::Ready(Some(Err(std::io::Error::new(
                        std::io::ErrorKind::Other,
                        "Iterator error",
                    ))))
                }
            }
        }
    }
}

#[inline]
fn convert_to_bytes(value: &Bound<'_, PyAny>) -> Option<Bytes> {
    // Optimized for SSE: most likely string with "data: ...\n\n"
    if let Ok(s) = value.downcast::<PyString>() {
        return Some(Bytes::from(s.to_string_lossy().into_owned()));
    }

    if let Ok(b) = value.downcast::<PyBytes>() {
        return Some(Bytes::copy_from_slice(b.as_bytes()));
    }

    // Try extract string
    if let Ok(s) = value.extract::<String>() {
        return Some(Bytes::from(s));
    }

    // Try __bytes__ method
    if let Ok(bobj) = value.call_method0("__bytes__") {
        if let Ok(b) = bobj.downcast::<PyBytes>() {
            return Some(Bytes::copy_from_slice(b.as_bytes()));
        }
    }

    // Last resort: str()
    if let Ok(s) = value.str() {
        return Some(Bytes::from(s.to_string()));
    }

    None
}

/// Create optimized streaming response
pub fn create_sse_response(
    content: Py<PyAny>,
) -> Result<actix_web::HttpResponse, actix_web::Error> {
    use actix_web::HttpResponse;

    let mut stream = PythonDirectStream::new(content);

    // Try to collect small responses
    if let Some(body) = stream.try_collect_small() {
        // Small response - send as single body
        return Ok(HttpResponse::Ok()
            .content_type("text/event-stream")
            .append_header(("Cache-Control", "no-cache"))
            .append_header(("X-Accel-Buffering", "no"))
            .body(body));
    }

    // Large response - use streaming
    Ok(HttpResponse::Ok()
        .content_type("text/event-stream")
        .append_header(("Cache-Control", "no-cache"))
        .append_header(("X-Accel-Buffering", "no"))
        .streaming(Box::pin(stream)))
}
