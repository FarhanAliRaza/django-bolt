"""Test that merged APIs preserve per-API logging configs"""
import pytest
from django_bolt import BoltAPI
from django_bolt.logging import LoggingConfig


def test_merged_api_preserves_logging_config():
    """Test that each handler uses its original API's logging config after merge"""
    # Create API 1 with custom logging
    logging_config_1 = LoggingConfig(
        logger_name="api1_logger",
        request_log_fields={"path", "client_ip"},
        response_log_fields={"status_code"},
    )
    api1 = BoltAPI(logging_config=logging_config_1)

    @api1.get("/api1")
    async def handler1():
        return {"api": 1}

    # Create API 2 with different logging
    logging_config_2 = LoggingConfig(
        logger_name="api2_logger",
        request_log_fields={"method", "path"},
        response_log_fields={"duration"},
    )
    api2 = BoltAPI(logging_config=logging_config_2)

    @api2.get("/api2")
    async def handler2():
        return {"api": 2}

    # Simulate merge (like runbolt does with handler_id renumbering)
    merged = BoltAPI(enable_logging=False)
    merged._handler_api_map = {}

    next_handler_id = 0

    # Merge routes from api1 (renumber handler_ids to avoid collisions)
    for method, path, old_handler_id, handler in api1._routes:
        new_handler_id = next_handler_id
        next_handler_id += 1
        merged._routes.append((method, path, new_handler_id, handler))
        merged._handlers[new_handler_id] = handler
        merged._handler_api_map[new_handler_id] = api1  # Store original API
        if handler in api1._handler_meta:
            merged._handler_meta[handler] = api1._handler_meta[handler]

    # Merge routes from api2 (renumber handler_ids to avoid collisions)
    for method, path, old_handler_id, handler in api2._routes:
        new_handler_id = next_handler_id
        next_handler_id += 1
        merged._routes.append((method, path, new_handler_id, handler))
        merged._handlers[new_handler_id] = handler
        merged._handler_api_map[new_handler_id] = api2  # Store original API
        if handler in api2._handler_meta:
            merged._handler_meta[handler] = api2._handler_meta[handler]

    merged._next_handler_id = next_handler_id

    # Verify: handler 0 (from api1) maps to api1
    handler_id_api1 = 0  # First route merged (from api1)
    print(f"Merged handler_ids: {list(merged._handler_api_map.keys())}")
    print(f"API1 object id: {id(api1)}, API2 object id: {id(api2)}")
    for hid, api in merged._handler_api_map.items():
        print(f"  handler_id={hid} -> API object id={id(api)}, logger={api._logging_middleware.config.logger_name if api._logging_middleware else None}")

    assert handler_id_api1 in merged._handler_api_map, f"handler_id {handler_id_api1} not in map"
    mapped_api1 = merged._handler_api_map[handler_id_api1]
    assert id(mapped_api1) == id(api1), f"Expected api1 (id={id(api1)}), got (id={id(mapped_api1)})"
    assert mapped_api1._logging_middleware.config.logger_name == "api1_logger"
    assert mapped_api1._logging_middleware.config.request_log_fields == {"path", "client_ip"}

    # Verify: handler 1 (from api2) maps to api2
    handler_id_api2 = 1  # Second route merged (from api2)
    assert handler_id_api2 in merged._handler_api_map, f"handler_id {handler_id_api2} not in map"
    mapped_api2 = merged._handler_api_map[handler_id_api2]
    assert id(mapped_api2) == id(api2), f"Expected api2 (id={id(api2)}), got (id={id(mapped_api2)})"
    assert mapped_api2._logging_middleware.config.logger_name == "api2_logger"
    assert mapped_api2._logging_middleware.config.request_log_fields == {"method", "path"}

    print("✓ Test passed: Merged API preserves per-API logging configs")


def test_deduplication_by_object_identity():
    """Test that duplicate API instances (same object) are deduplicated"""
    # Create one API
    api1 = BoltAPI()

    @api1.get("/test")
    async def handler():
        return {"test": True}

    # Simulate autodiscovery finding the SAME api object twice
    apis = [
        ("testproject.api:api", api1),
        ("testproject.api:api", api1),  # Same object, different path (shouldn't happen but test it)
    ]

    # Deduplicate
    seen_ids = set()
    deduplicated = []
    for api_path, api in apis:
        api_id = id(api)
        if api_id not in seen_ids:
            seen_ids.add(api_id)
            deduplicated.append((api_path, api))

    # Should only have 1 entry
    assert len(deduplicated) == 1
    assert deduplicated[0] == ("testproject.api:api", api1)

    print("✓ Test passed: Deduplication works correctly")


if __name__ == "__main__":
    test_merged_api_preserves_logging_config()
    test_deduplication_by_object_identity()
    print("\n✅ All tests passed!")
