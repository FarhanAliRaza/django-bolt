/// Permission guards for authorization checks
///
/// Guards are evaluated after authentication to determine if a request
/// should be allowed. This happens in Rust for zero-GIL overhead.
use crate::middleware::auth::AuthContext;

/// Guard/permission types
#[derive(Debug, Clone)]
pub enum Guard {
    AllowAny,
    IsAuthenticated,
    IsSuperuser,
    IsStaff,
    HasPermission(String),
    HasAnyPermission(Vec<String>),
    HasAllPermissions(Vec<String>),
}

/// Evaluate guards against an optional AuthContext
/// Returns true if all guards pass, false otherwise
pub fn evaluate_guards(guards: &[Guard], auth_ctx: Option<&AuthContext>) -> GuardResult {
    // If no guards configured, allow by default
    if guards.is_empty() {
        return GuardResult::Allow;
    }

    // Check each guard
    for guard in guards {
        match guard {
            Guard::AllowAny => {
                // AllowAny short-circuits - allow immediately
                return GuardResult::Allow;
            }
            Guard::IsAuthenticated => {
                if auth_ctx.is_none() || auth_ctx.unwrap().user_id.is_none() {
                    return GuardResult::Unauthorized;
                }
            }
            Guard::IsSuperuser => match auth_ctx {
                None => return GuardResult::Unauthorized,
                Some(ctx) => {
                    if !ctx.is_superuser {
                        return GuardResult::Forbidden;
                    }
                }
            },
            Guard::IsStaff => match auth_ctx {
                None => return GuardResult::Unauthorized,
                Some(ctx) => {
                    if !ctx.is_staff {
                        return GuardResult::Forbidden;
                    }
                }
            },
            Guard::HasPermission(perm) => match auth_ctx {
                None => return GuardResult::Unauthorized,
                Some(ctx) => {
                    if !ctx.permissions.contains(perm) {
                        return GuardResult::Forbidden;
                    }
                }
            },
            Guard::HasAnyPermission(perms) => match auth_ctx {
                None => return GuardResult::Unauthorized,
                Some(ctx) => {
                    if !perms.iter().any(|p| ctx.permissions.contains(p)) {
                        return GuardResult::Forbidden;
                    }
                }
            },
            Guard::HasAllPermissions(perms) => match auth_ctx {
                None => return GuardResult::Unauthorized,
                Some(ctx) => {
                    if !perms.iter().all(|p| ctx.permissions.contains(p)) {
                        return GuardResult::Forbidden;
                    }
                }
            },
        }
    }

    GuardResult::Allow
}

/// Result of guard evaluation
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GuardResult {
    Allow,
    Unauthorized, // 401 - not authenticated
    Forbidden,    // 403 - authenticated but lacking permission
}
