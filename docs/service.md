# Speed up startup with the local API service

With a 0.3.0 binding, set `NATIVELANG_CLASSIFY_SERVICE=1` and use the usual classification call. The first call starts the service, downloads the model if needed, and waits for it to load. Later processes under the same user account reuse that model. The service releases it after 15 minutes with no requests.

For the 0.2.x bindings, use the [standalone HTTP server](../self-hosting/README.md).

## Start, stop or check the service

The first service-enabled call installs the control executable in the `.nativelang/classify/bin` directory in your home folder. Run these commands from that folder (use `.\classify.exe` in PowerShell), or add it to your PATH to use `classify` anywhere.

```sh
./classify service start
./classify service status
./classify service stop
./classify service logs
```

Stopping releases the model. A later service-enabled call starts it again. Unset `NATIVELANG_CLASSIFY_SERVICE` to use a worker in the calling application.

## Port and discovery

The service listens on a loopback port assigned by the OS. Set `NATIVELANG_CLASSIFY_PORT` to request a specific port, for example `9090`. Stop an existing service before changing its port. If your chosen port is busy, unset the variable to let the OS choose.

The service writes its address, PID, process start time and TLS certificate fingerprint to `~/.nativelang/classify/service/endpoint.json`. Each client verifies the certificate before sending credentials or text. Concurrent callers coordinate startup. Recovery uses the OS manager's registration to identify the Classify process.

## Lifecycle and diagnostics

macOS runs a user LaunchAgent, Linux uses a systemd user service, and Windows uses an on-demand task under the signed-in user. Where the OS disallows a background job, the binding can run inference in its own process. The service log records the reason.

`status` reports download progress, readiness, PID and address. While running, it includes model load time, request and error counts, and total inference time in milliseconds. Counters reset on restart. `logs` shows lifecycle events and hardware selection. Diagnostics stay on the machine and omit request text and category labels.
