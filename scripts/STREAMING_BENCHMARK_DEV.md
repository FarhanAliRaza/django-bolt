# It is advised to use Async Streaming when possible. It can handle more requests and also do not have threads limit.

## Async Streaming

Test completed in 66.88s

======================================================================
RESULTS
======================================================================

Total Clients: 10000
Successful: 10000 (100.0%)
Failed: 0 (0.0%)

Message Delivery:
Total Messages: 572,919
Avg Messages/Client: 57.3
StDev: 0.5
Min/Max: 57/58

Data Transfer:
Total Bytes: 14,743,590 (14.06 MB)
Avg Bytes/Client: 1,474
Throughput: 0.00 MB/s

Connection Duration:
Avg Duration: 60.38s
StDev: 0.25s
Min/Max: 60.01s / 60.81s

Messaging Rate:
Avg Messages/sec/client: 0.95
Total Messages/sec: 9489.33

Resource Usage:
Memory: 236.1 MB
CPU (current): 94.2%
CPU (avg during test): 11.9%
CPU (min/max during test): 0.0% / 101.9%

======================================================================

## Sync Streaming

By default sync streaming is limited to 1000 threads to prevent threads exhaustion. So it can handle
1000 concurrent connection without any issue. For setting it to 5000 `DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS = 5000` add this line to settings. You can add any number according to your system.

With number set to 10000 threads.

## For 20 Second load time

Test completed in 26.87s

======================================================================
RESULTS
======================================================================

Total Clients: 10000
Successful: 10000 (100.0%)
Failed: 0 (0.0%)

Message Delivery:
Total Messages: 170,784
Avg Messages/Client: 17.1
StDev: 0.3
Min/Max: 17/18

Data Transfer:
Total Bytes: 4,395,491 (4.19 MB)
Avg Bytes/Client: 440
Throughput: 0.00 MB/s

Connection Duration:
Avg Duration: 20.36s
StDev: 0.19s
Min/Max: 20.05s / 21.12s

Messaging Rate:
Avg Messages/sec/client: 0.84
Total Messages/sec: 8389.48

Resource Usage:
Memory: 234.4 MB
CPU (current): 102.1%
CPU (avg during test): 18.6%
CPU (min/max during test): 0.0% / 98.1%

======================================================================
