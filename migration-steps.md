# How to migrate

> **NOTE** if using docker, make sure to stop all pods first so no changes occur during migration

1) create ansible playbook to copy all the files and folder

2) Create the neccessary pvc volumes needed

3) attach to the `pvc-config-dummy-pod`, which uses a busybox image.

4) You will then run the commands `kubectl cp <local_folder_path> <namespace>/busybox-copier:/mnt/<folder>`

This will prepare everything you need so you can just start attaching it to the deployment and start using it, you will just need to map the volume to the right directory



