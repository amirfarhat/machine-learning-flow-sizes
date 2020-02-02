#!/usr/bin/env python
import os
from ctypes import *
import numpy as np
import pickle 
 
# loads nvidia nvml library 
nvml = CDLL('libnvidia-ml.so')

nvmlReturn_t = c_int
nvmlInit = nvml.nvmlInit
nvmlInit.restype = nvmlReturn_t
nvmlInit.argtypes = ()
NVML_SUCCESS = 0  # enum that checks whether nvml queries are successful
assert(NVML_SUCCESS == nvmlInit()) # initialize nvml 

# define function as variable (restype = return type && argtypes = argument types)
nvmlDeviceGetCount = nvml.nvmlDeviceGetCount
nvmlDeviceGetCount.restype = nvmlReturn_t
nvmlDeviceGetCount.argtypes = (POINTER(c_uint),)

# c returns function values in parameters and takes arguments as pointers, not actual objects
# count of accessible devices in system
device_count = c_uint()
assert(NVML_SUCCESS == nvmlDeviceGetCount(pointer(device_count)))
device_count = device_count.value

nvmlDevice_t = c_void_p
devices = [nvmlDevice_t() for i in range(device_count)]  # list of "null" types for number of devices
NVML_DEVICE_NAME_BUFFER_SIZE = 64
name_t = c_char * NVML_DEVICE_NAME_BUFFER_SIZE
names = [name_t() for i in range(device_count)]  # list of "chars" with size 64 for number of devices
nvlink_count = [c_uint() for i in range(device_count)]  # list of "u_ints" for number of devices
NVML_NVLINK_MAX_LINKS = 6
nvlink_target = [[c_uint() for j in range(NVML_NVLINK_MAX_LINKS)] for i in range(device_count)]  # nested list with maximum number of nvlinks

NVML_DEVICE_PCI_BUS_ID_BUFFER_V2_SIZE = 16
NVML_DEVICE_PCI_BUS_ID_BUFFER_SIZE = 32


#  struct is user defined data type that lets you group items of possibly different types into a single type
class nvmlPciInfo_t(Structure):
    _fields_ = [
        ('busIdLegacy', c_char*NVML_DEVICE_PCI_BUS_ID_BUFFER_V2_SIZE),
        ('domain', c_uint),
        ('bus', c_uint),
        ('device', c_uint),
        ('pciDeviceId', c_uint),
        ('pciSubSystemId', c_uint),
        ('busId', c_char*NVML_DEVICE_PCI_BUS_ID_BUFFER_SIZE)
    ]

pci_infos = [nvmlPciInfo_t() for i in range(device_count)]  # list of nvmlPciInfo_t objects for number of devices
counter_index = 0

# function that returns the device handle for specific GPU based on index
nvmlDeviceGetHandleByIndex = nvml.nvmlDeviceGetHandleByIndex
nvmlDeviceGetHandleByIndex.restype = nvmlReturn_t
nvmlDeviceGetHandleByIndex.argtypes = (c_uint, POINTER(c_void_p))

class nvmlFieldValue_t(Structure):
    _fields_ = [
        ('fieldId', c_uint),
        ('unused', c_uint),
        ('timestamp', c_longlong),
        ('latencyUsec', c_longlong),
        ('valueType', c_int),
        ('nvmlReturn', nvmlReturn_t),
        ('value', c_uint), #nvmlValue_t),
    ]

NVML_FI_DEV_NVLINK_LINK_COUNT = 91
NVML_VALUE_TYPE_UNSIGNED_INT = 1

# field values 
nvmlDeviceGetFieldValues = nvml.nvmlDeviceGetFieldValues
nvmlDeviceGetFieldValues.restype = nvmlReturn_t
nvmlDeviceGetFieldValues.argtypes = (nvmlDevice_t, c_uint, POINTER(nvmlFieldValue_t))

# device names 
nvmlDeviceGetName = nvml.nvmlDeviceGetName
nvmlDeviceGetName.restype = nvmlReturn_t
nvmlDeviceGetName.argtypes = (nvmlDevice_t, c_char_p, c_uint)

# pci info 
nvmlDeviceGetPciInfo = nvml.nvmlDeviceGetPciInfo
nvmlDeviceGetPciInfo.restype = nvmlReturn_t
nvmlDeviceGetPciInfo.argtypes = (nvmlDevice_t, POINTER(nvmlPciInfo_t))

# check number of nvlinks for each of the devices
for i in range(device_count):
    assert NVML_SUCCESS == nvmlDeviceGetHandleByIndex(i, pointer(devices[i]))
    value = nvmlFieldValue_t()
    value.fieldId = NVML_FI_DEV_NVLINK_LINK_COUNT
    assert NVML_SUCCESS == nvmlDeviceGetFieldValues(devices[i], 1, pointer(value))
    assert NVML_SUCCESS == value.nvmlReturn
    assert value.valueType == NVML_VALUE_TYPE_UNSIGNED_INT
    nvlink_count[i] = value.value #.uiVal
    assert NVML_SUCCESS == nvmlDeviceGetName(devices[i], names[i], NVML_DEVICE_NAME_BUFFER_SIZE)
    print("GPU%d: %r; %d nvlinks" % (i, names[i].value.decode(), nvlink_count[i]))
    assert NVML_SUCCESS == nvmlDeviceGetPciInfo(devices[i], pointer(pci_infos[i]))

nvmlNvLinkCapability_t = c_int

# retrieves requested capabilities
nvmlDeviceGetNvLinkCapability = nvml.nvmlDeviceGetNvLinkCapability
nvmlDeviceGetNvLinkCapability.restype = nvmlReturn_t
nvmlDeviceGetNvLinkCapability.argtypes = (nvmlDevice_t, c_uint, nvmlNvLinkCapability_t, POINTER(c_uint))
NVML_NVLINK_CAP_P2P_SUPPORTED = 0

# retrieves remote nvlink node pci info
nvmlDeviceGetNvLinkRemotePciInfo = nvml.nvmlDeviceGetNvLinkRemotePciInfo
nvmlDeviceGetNvLinkRemotePciInfo.restype = nvmlReturn_t
nvmlDeviceGetNvLinkRemotePciInfo.argtypes = (nvmlDevice_t, c_uint, POINTER(nvmlPciInfo_t))

# acquire handle for a particular degice based on its PCI bus id
nvmlDeviceGetHandleByPciBusId = nvml.nvmlDeviceGetHandleByPciBusId
nvmlDeviceGetHandleByPciBusId.restype = nvmlReturn_t
nvmlDeviceGetHandleByPciBusId.argtypes = (c_char_p, POINTER(nvmlDevice_t))

# get nvml device index
nvmlDeviceGetIndex = nvml.nvmlDeviceGetIndex
nvmlDeviceGetIndex.restype = nvmlReturn_t
nvmlDeviceGetIndex.argtypes = (nvmlDevice_t, POINTER(c_uint))

# checks that nvlinks are properly connected
for i in range(device_count):
    for k in range(nvlink_count[i]):
        cap_result = c_uint()
        assert NVML_SUCCESS == nvmlDeviceGetNvLinkCapability(devices[i], k, NVML_NVLINK_CAP_P2P_SUPPORTED, pointer(cap_result))
        assert cap_result
        pci_info_remote = nvmlPciInfo_t()
        assert NVML_SUCCESS == nvmlDeviceGetNvLinkRemotePciInfo(devices[i], k, pointer(pci_info_remote))
        remoteDevice = nvmlDevice_t()
        remoteBusId = pci_info_remote.busIdLegacy
        assert NVML_SUCCESS == nvmlDeviceGetHandleByPciBusId(remoteBusId, pointer(remoteDevice))
        assert NVML_SUCCESS == nvmlDeviceGetIndex(remoteDevice, pointer(nvlink_target[i][k]))
        nvlink_target[i][k] = nvlink_target[i][k].value

# get nvlink utilization counters
nvmlDeviceGetNvLinkUtilizationCounter = nvml.nvmlDeviceGetNvLinkUtilizationCounter
nvmlDeviceGetNvLinkUtilizationCounter.restype = nvmlReturn_t
nvmlDeviceGetNvLinkUtilizationCounter.argtypes = (nvmlDevice_t, c_uint, c_uint, POINTER(c_ulonglong), POINTER(c_ulonglong))

N_TRIALS = 1000

rx = c_ulonglong()
tx = c_ulonglong()
prx, ptx = pointer(rx), pointer(tx)

rx_samples = np.zeros((N_TRIALS, device_count, NVML_NVLINK_MAX_LINKS), np.uint64)
tx_samples = np.zeros((N_TRIALS, device_count, NVML_NVLINK_MAX_LINKS), np.uint64)

link_sample_order = np.full((device_count, NVML_NVLINK_MAX_LINKS), -1, int)
order = 0
for i in range(device_count):
    device = devices[i]
    for k in range(nvlink_count[i]):
        link_sample_order[i,k] = order
        order += 1

import time
t_old = time.time()
time_stamps = np.empty((N_TRIALS+1,), np.float64)


for n in range(N_TRIALS):
    time_stamps[n] = time.time()
    for i in range(device_count):
        device = devices[i]
        for k in range(nvlink_count[i]):
            #if nvlink_target[i][k] ==0:
                assert NVML_SUCCESS == nvmlDeviceGetNvLinkUtilizationCounter(device, k, counter_index, prx, ptx)
                rx_samples[n,i,k] = rx.value
                tx_samples[n,i,k] = tx.value

time_stamps[-1] = time.time()

dtime_stamps = np.diff(time_stamps)
eval_times = dtime_stamps[:,None,None] * (link_sample_order / order)[None,:,:]

midpoint_times = (time_stamps[:-1] + time_stamps[1:]) * .5

rx_samples_interp = np.zeros((N_TRIALS, device_count, NVML_NVLINK_MAX_LINKS), np.float64)
tx_samples_interp = np.zeros((N_TRIALS, device_count, NVML_NVLINK_MAX_LINKS), np.float64)
for i in range(device_count):
    for k in range(nvlink_count[i]):
        rx_samples_interp[:,i,k] = np.interp(midpoint_times, time_stamps[:-1] + eval_times[:,i,k], rx_samples[:,i,k])
        tx_samples_interp[:,i,k] = np.interp(midpoint_times, time_stamps[:-1] + eval_times[:,i,k], tx_samples[:,i,k])

#rx_rates = np.diff(rx_samples_interp, axis=0) / np.diff(midpoint_times)[:,None,None]
#
#tx_rates = np.diff(tx_samples_interp, axis=0) / np.diff(midpoint_times)[:,None,None]
#
#TM = np.zeros((2, N_TRIALS-1, device_count, device_count), np.float64)
#for i in range(device_count):
#    for k in range(nvlink_count[i]):
#        TM[0,:,i,nvlink_target[i][k]] += rx_rates[:,i,k]
#        TM[1,:,i,nvlink_target[i][k]] += tx_rates[:,i,k]
#print(TM)
#np.save('TM.npy', TM)
rx_counts = np.diff(rx_samples, axis=0)
tx_counts = np.diff(tx_samples, axis=0)
print('no interpolation')
#rx_counts = np.diff(rx_samples_interp, axis=0)
#tx_counts = np.diff(tx_samples_interp, axis=0)

TM = np.zeros((2, N_TRIALS-1, device_count, device_count), np.float64)
for i in range(device_count):
    for k in range(nvlink_count[i]):
        TM[0,:,i,nvlink_target[i][k]] += rx_counts[:,i,k]
        TM[1,:,i,nvlink_target[i][k]] += tx_counts[:,i,k]

counters = {'timestamp': midpoint_times, 'tm': TM}
with open('counters.pkl', 'wb') as f:
    pickle.dump(counters, f)
#import pdb
#pdb.set_trace()


t_new = time.time()
t_elapsed = t_new - t_old
print("Elapsed time per interrogation of all links in both directions: %.6f" % (t_elapsed / N_TRIALS,))

for i in range(device_count):
    for j in range(device_count):
        if j==i:
            print("%-4s" % (" X ",), end='')
        else:
            links = 0
            for k in range(nvlink_count[i]):
                links += (nvlink_target[i][k] == j)
            print("NV%d " % (links,), end='')
    print()

# shutdown nvml object module
nvmlShutdown = nvml.nvmlShutdown
nvmlShutdown.restype = nvmlReturn_t
nvmlShutdown.argtypes = ()

nvmlShutdown()

