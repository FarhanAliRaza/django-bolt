/// Fast header lookup using perfect hash
///
/// Inspired by Bun's perfect hash approach for HTTP headers.
/// Common headers are looked up using a compile-time perfect hash (O(1))
/// before falling back to HashMap lookup for custom headers.

use phf::phf_map;

/// Header index for O(1) lookups of common headers
/// These indices correspond to common HTTP headers we want to fast-path
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum CommonHeader {
    Authorization = 0,
    ContentType = 1,
    ContentLength = 2,
    Accept = 3,
    AcceptEncoding = 4,
    AcceptLanguage = 5,
    CacheControl = 6,
    Connection = 7,
    Cookie = 8,
    Host = 9,
    Origin = 10,
    Referer = 11,
    UserAgent = 12,
    XForwardedFor = 13,
    XRealIp = 14,
    XApiKey = 15,
    IfNoneMatch = 16,
    IfModifiedSince = 17,
    Range = 18,
}

/// Perfect hash map for common HTTP headers (lowercase)
/// Generated at compile-time, zero runtime cost
static COMMON_HEADERS: phf::Map<&'static str, CommonHeader> = phf_map! {
    "authorization" => CommonHeader::Authorization,
    "content-type" => CommonHeader::ContentType,
    "content-length" => CommonHeader::ContentLength,
    "accept" => CommonHeader::Accept,
    "accept-encoding" => CommonHeader::AcceptEncoding,
    "accept-language" => CommonHeader::AcceptLanguage,
    "cache-control" => CommonHeader::CacheControl,
    "connection" => CommonHeader::Connection,
    "cookie" => CommonHeader::Cookie,
    "host" => CommonHeader::Host,
    "origin" => CommonHeader::Origin,
    "referer" => CommonHeader::Referer,
    "user-agent" => CommonHeader::UserAgent,
    "x-forwarded-for" => CommonHeader::XForwardedFor,
    "x-real-ip" => CommonHeader::XRealIp,
    "x-api-key" => CommonHeader::XApiKey,
    "if-none-match" => CommonHeader::IfNoneMatch,
    "if-modified-since" => CommonHeader::IfModifiedSince,
    "range" => CommonHeader::Range,
};

/// Fast header storage that uses an array for common headers
/// and a HashMap for custom headers
pub struct FastHeaders {
    /// Array of common headers (indexed by CommonHeader enum)
    /// Uses Option to indicate presence
    common: [Option<String>; 19], // Must match number of CommonHeader variants

    /// Fallback HashMap for custom headers
    custom: ahash::AHashMap<String, String>,
}

impl FastHeaders {
    #[inline]
    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            common: Default::default(),
            custom: ahash::AHashMap::with_capacity(capacity),
        }
    }

    /// Insert a header with fast-path for common headers
    #[inline]
    pub fn insert(&mut self, name: String, value: String) {
        // Try perfect hash lookup first
        if let Some(&header_idx) = COMMON_HEADERS.get(&name) {
            // Store in fixed array for O(1) access
            self.common[header_idx as usize] = Some(value);
        } else {
            // Store in HashMap for custom headers
            self.custom.insert(name, value);
        }
    }

    /// Convert to AHashMap (for backwards compatibility)
    pub fn into_hashmap(self) -> ahash::AHashMap<String, String> {
        let mut map = self.custom;

        for (name, idx) in COMMON_HEADERS.entries() {
            if let Some(value) = self.common[*idx as usize].clone() {
                map.insert(name.to_string(), value);
            }
        }

        map
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_into_hashmap() {
        let mut headers = FastHeaders::with_capacity(10);
        headers.insert("authorization".to_string(), "Bearer token".to_string());
        headers.insert("x-custom".to_string(), "value".to_string());

        let map = headers.into_hashmap();
        assert_eq!(map.get("authorization"), Some(&"Bearer token".to_string()));
        assert_eq!(map.get("x-custom"), Some(&"value".to_string()));
    }
}
