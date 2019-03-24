import collections

import codec
import ramdisk


Codecs = collections.OrderedDict([
        ('None',     codec.Codec),
        ('RAMDisk',  ramdisk.RAMDisk),
])
