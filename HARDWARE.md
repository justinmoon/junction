# HWI

`path` key is always present. It's a marker for how desktop communicates with the device.

`fingerprint` identifies the master private key on the device. It's only present if the device is unlocked, and since it's only 4 bytes there can be collisions (1 in 4,294,967,296).


