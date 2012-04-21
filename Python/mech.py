# mech.py

DISTANCE_A = 1.0 # inch
DISTANCE_B = 1.25 # inch
DISTANCE_C = 3.25 # inch
X_STEP_TO_INCH = 200/.2
Y_STEP_TO_INCH = 200/.2
Z_STEP_TO_INCH = 200/.125
PAN_ANGLE_TO_PERCENT = 1.0 / 360
TILT_ANGLE_TO_PERCENT = 1.0 / 90
STEPS_PER_PIXEL = 3
FEED_RATE = 100 # in steps/s
HOST = '169.254.1.1'
PORT = 2000

import math
import socket
import os
import time
import wx
import wx.lib.delayedresult as delayedresult
from binascii import hexlify, unhexlify
from struct import pack, unpack


class Convert:

  def percent_to_angle(cls, percent, axis='pan'):
    return percent / cls._get_factor(axis)

  def angle_to_percent(cls, angle, axis='pan'):
    return angle * cls._get_factor(axis)

  def step_to_unit(cls, step, unit='in', axis='x'):
    return float(step) / cls._get_factor(axis, unit)

  def unit_to_step(cls, num, unit='in', axis='x'):
    return long(num * cls._get_factor(axis, unit))

  def _get_factor(cls, axis, unit='in'):
    if axis in 'xX':
      factor = X_STEP_TO_INCH
    elif axis in 'yY':
      factor = Y_STEP_TO_INCH
    elif axis in 'zZ':
      factor = Z_STEP_TO_INCH
    elif axis == 'pan':
      factor = PAN_ANGLE_TO_PERCENT
    elif axis == 'tilt':
      factor = TILT_ANGLE_TO_PERCENT
    if unit == 'mil':
      factor /= 1000
    elif unit == 'mm':
      factor /= 25.4
    elif unit == 'step':
      factor = 1
    return factor


class Machine:
  """The class that will send data to the machine."""

  def __init__(self, *args, **kargs):
    self.parent = args[0]
    self.update_status = self.parent.sb.SetStatusText
    self.read_status = self.parent.sb.GetStatusText
    self.com = Communicate(self)
    self.p1 = None
    self.p2 = None
    self.p3 = None
    self.base = None
    self.height = None
    self.normal = None
    self.units = 'in'
    self.xyz = (0,0,0)
    self.pan_angle = .5
    self.tilt_angle = 0

  def all_points_defined(self):
    return self.base and self.height

  def draw(self, use_solenoid, img=None):
    """Sends the machine the command to draw the image"""
    pan = self._constrain_num(convert.angle_to_percent(self.normal.phi(),
                                                          'pan'), (0,1))
    tilt = self._constrain_num(convert.angle_to_percent(self.normal.theta(),
                                                           'tilt'), (0,1))

    xyz = self._real_xyz_to_machine_xyz(self.p1.tuple())
    xyz = self._tuple_to_step(xyz)
    base = self._real_xyz_to_machine_xyz(self.base.tuple())
    base = self._tuple_to_step(base)
    height = self._real_xyz_to_machine_xyz(self.height.tuple())
    height = self._tuple_to_step(height)
    self.com.send_g01(xyz + (pan, tilt), blocking=True)
    if use_solenoid:
      self.com.send_g03(base, height, img.resize(self.get_pic_pixel_count()))
    else:
      self.com.send_g02(base, height)

  def get_longest_side_size(self):
    """Returns the size in steps of the picture."""
    base = Vector(self._tuple_to_step(self.base.tuple()))
    height = Vector(self._tuple_to_step(self.height.tuple()))
    return (base.longest(), height.longest())

  def get_pic_pixel_count(self):
    """Returns the size in pixels of the picture"""
    return ([x / STEPS_PER_PIXEL for x in self.get_longest_side_size()])

  def get_pic_size(self):
    """Get the size of the picture to be drawn"""
    if self.all_points_defined():
      return (self.base.length(), self.height.length(), self.units)
    else:
      return None

  def get_real_xyz(self):
    """Convert machine xyz to real world xyz"""
    theta = convert.percent_to_angle(self.pan_angle, 'pan') * math.pi / 180
    phi = convert.percent_to_angle(self.tilt_angle, 'tilt') * math.pi / 180
    x, y, z = self._step_to_tuple(self.xyz)
    x = x + math.sin(theta)*(DISTANCE_A + DISTANCE_B * math.cos(phi) +
                                       DISTANCE_C * math.sin(phi))
    y = y + math.cos(theta)*(DISTANCE_A + DISTANCE_B * math.cos(phi) +
                                       DISTANCE_C * math.sin(phi))
    z = z + DISTANCE_B * math.sin(phi) + DISTANCE_C * math.cos(phi)
    return (x, y, z)
    
  def set_points(self, p1=None, p2=None, p3=None):
    """Set the points for the machine.
    p1 and p2 determine the base, p3 determines the height
    """
    if p1 != None:
      self.p1 = Vector(p1)
    if p2 != None:
      self.p2 = Vector(p2)
    if p3 != None:
      self.p3 = Vector(p3)
    if self._plane_points_defined():
      self.base = self.p2 - self.p1
      self.height = self.p3 - self.p1
      if self.height.length() != 0:
        self.height -= self.base.proj(self.height)
        self.parent.plane_points.update_size_text()
        self.normal = self.base.cross(self.height)
        if self.normal.theta() > 90:
          self.normal = -self.normal
        print "Size: " + str(self.base) + ", " + str(self.height)
        print self.normal.theta()
        print self.normal.phi()
      else:
        self.height = None

  def jog(self, axis, num, unit = 'step'):
    """Moves num units in axis direction"""
    if axis in 'xX':
      num = convert.unit_to_step(num, unit, axis)
      self.com.send_g00((num, 0, 0))
    elif axis in 'yY':
      num = convert.unit_to_step(num, unit, axis)
      self.com.send_g00((0, num, 0))
    elif axis in 'zZ':
      num = convert.unit_to_step(num, unit, axis)
      self.com.send_g00((0, 0, num))
    elif axis in 'Panpan':
      oldang = convert.percent_to_angle(self.pan_angle, 'pan')
      num = convert.angle_to_percent(oldang + num, axis)
      num = self._constrain_num(num, (0,1))
      self.com.send_g04(num)
      self.pan_angle = num
    elif axis in 'Tiltilt':
      oldang = convert.percent_to_angle(self.tilt_angle, 'tilt')
      num = convert.angle_to_percent(oldang + num, axis)
      num = self._constrain_num(num, (0,1))
      self.com.send_g05(num)
      self.tilt_angle = num

  def move(self, values):
    """Moves machine in absolute, rather than relative"""
    xyz = self._real_xyz_to_machine_xyz(values[:3])
    xyz = self._tuple_to_step(xyz)
    pan = convert.angle_to_percent(values[3], 'pan')
    pan = self._constrain_num(pan, (0,1))
    self.pan_angle = pan
    tilt = convert.angle_to_percent(values[4], 'tilt')
    tilt = self._constrain_num(tilt, (0,1))
    self.tilt_angle = tilt
    self.com.send_g01(xyz + (pan, tilt))

  def set_status_function(self, f):
    """Set the function that allows you to change the status bar"""
    self.update_status = f

  def set_units(self, units):
    """Change the units to a new type"""
    self.units = units
    #send event

  def set_bitmap(self, pic):
    self.pic = pic

  def stop(self):
    """Tells the machine to stop moving the stepper motors"""
    self.com.send_g0a();

  def update_positions(self, values):
    """Tells the position panel to update everything"""
    print 'We got ' + repr(values)
    self.pan_angle = values[3]
    self.tilt_angle = values[4]
    self.xyz = values[:3]
    x, y, z = self.get_real_xyz()
    pan = convert.percent_to_angle(self.pan_angle, 'pan')
    tilt = convert.percent_to_angle(self.tilt_angle, 'tilt')
    self.parent.positions.update((x, y, z, pan, tilt))

  def _constrain_num(self, x, range):
    if x < range[0]:
      return 0
    elif x > range[1]:
      return 1
    else:
      return x

  def _get_img_data(self):
    return self.pic.resize(get_pic_size()[:2]).convert('1')

  def _real_xyz_to_machine_xyz(self, real_xyz):
    theta = convert.percent_to_angle(self.pan_angle, 'pan') * math.pi / 180
    phi = convert.percent_to_angle(self.tilt_angle, 'tilt') * math.pi / 180
    x, y, z = real_xyz
    x = x - math.sin(theta)*(DISTANCE_A + DISTANCE_B * math.cos(phi) +
                                       DISTANCE_C * math.sin(phi))
    y = y - math.cos(theta)*(DISTANCE_A + DISTANCE_B * math.cos(phi) +
                                       DISTANCE_C * math.sin(phi))
    z = z - DISTANCE_B * math.sin(phi) + DISTANCE_C * math.cos(phi)
    return (x, y, z)
  
  def _plane_points_defined(self):
    return self.p1 and self.p2 and self.p3

  def _tuple_to_step(self, tuple):
    """We'll use this in the final step to convert to steps"""
    return (convert.unit_to_step(tuple[0], self.units, 'x'),
            convert.unit_to_step(tuple[1], self.units, 'y'),
            convert.unit_to_step(tuple[2], self.units, 'z'))

  def _step_to_tuple(self, tuple):
    """Converting back the other way"""
    return (convert.step_to_unit(tuple[0], self.units, 'x'),
            convert.step_to_unit(tuple[1], self.units, 'y'),
            convert.step_to_unit(tuple[2], self.units, 'z'))


class Communicate:
  """This class handles the low-level communication details."""

  def __init__(self, machine):
    self.m = machine
    self.sending_command = False
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connect()

  def connect(self):
    """Attempt to connect to the WiFly"""
    if '169.254.' not in socket.gethostbyname(socket.gethostname()):
      self.m.update_status("Improper IP Address", 1)
    else:
      try:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.m.update_status("Connected to mBed", 1)
      except socket.error, msg:
        self.m.update_status("No Communication", 1)

  def check_ip(self):
    if '169.254.' not in socket.gethostbyname(socket.gethostname()):
      self.m.update_status("Improper IP Address", 1)
    elif "Improper IP Address" in self.m.read_status():
      self.m.update_status("IP Address in proper subnet", 1)

  def disconnect(self):
    self.s.close()

  def _send_response(self, delayed_result):
    id = delayed_result.getJobID()
    result = delayed_result.get()
    if isinstance(result, str):
      args = result.split(' ')
      if len(args) == 6:
        x = unpack('l', unhexlify(args[1]))
        y = unpack('l', unhexlify(args[2]))
        z = unpack('l', unhexlify(args[3]))
        pan = unpack('f', unhexlify(args[4]))
        tilt = unpack('f', unhexlify(args[5]))
        self.m.update_positions(x + y + z + pan + tilt)

  def send_g00(self, location):
    """Move relative to current position"""
    self.async_send('g00', location)

  def send_g01(self, location, blocking=False):
    """Move based on absolute position"""
    if not blocking:
      self.async_send('g01', location, 'lllff')
    else:
      self.blocking_send('g01', location, 'lllff')

  def send_g02(self, p1, p2):
    """Send the information to go along the path for the image"""
    self.async_send('g02', p1 + p2)

  def send_g03(self, p1, p2, img):
    """Send all the information needed to make the image"""
    self.send_image(img)
    self.async_send('g03', p1 + p2)

  def send_g04(self, angle, blocking=False):
    """Send pan angle change command to machine"""
    if not blocking:
      self.async_send('g04', (angle,), 'f')
    else:
      self.blocking_send('g04', (angle,), 'f')

  def send_g05(self, angle, blocking=False):
    """Send tilt angle change command to machine"""
    if not blocking:
      self.async_send('g05', (angle,), 'f')
    else:
      self.blocking_send('g05', (angle,), 'f')

  def send_g06(self, duty, hz):
    """Send solenoid pwm command to the machine"""
    self.async_send('g06', duty + hz, 'f')

  def send_g07(self, time):
    """Send command to turn on the solenoid for time ms"""
    self.async_send('g07', (time,))

  def send_g08(self):
    """Get positions and angles"""
    self.async_send('g08')

  def send_g0a(self, e=None):
    """Stop everything"""
    self.async_send('g0a')

  def async_send(self, msg_id, msg_data=(), datatype='l'):
    """Create a thread to do the sync without stalling the gui"""
    if not self.sending_command:
      if len(datatype) == 1:
        data_str = msg_id + ' ' + ' '.join([hexlify(pack(datatype, x))
                                            for x in msg_data])
      else:
        data_str = msg_id
        for i in range(len(datatype)):
          data_str += ' ' + hexlify(pack(datatype[i], msg_data[i]))
      delayedresult.startWorker(self._send_response, self.send,
                                wargs=(data_str,), jobID=msg_id)
    else:
      self.m.update_status("Command in progress", 0)

  def blocking_send(self, msg_id, msg_data=(), datatype='l'):
    """Send the sync, waiting until done"""
    if len(datatype) == 1:
      data_str = msg_id + ' ' + ' '.join([hexlify(pack(datatype, x))
                                          for x in msg_data])
    else:
      data_str = msg_id
      for i in range(len(datatype)):
        data_str += ' ' + hexlify(pack(datatype[i], msg_data[i]))
    self.send(data_str)

  def send(self, msg):
    """Send the message to the machine"""
    try:
      self.connect()
      self.m.update_status("Sending to mBed: " + repr(msg), 0)
      self.s.send(msg)
      self.m.update_status("Sent to mBed: " + repr(msg), 0)
      data = self.s.recv(1024)
      self.m.update_status("Command completed", 0)
      self.disconnect()
      return data
    except socket.error, errormsg:
      self.m.update_status("Failure to send: " + repr(msg), 0)
 
  def send_image(self, img):
    """Send the image to the machine, ASCII encoded in base 16"""
    img.convert('1').save('.temp', 'bmp')
    with open('.temp', 'rb') as f:
      data = hexlify(f.read())
      try:
        self.connect()
        for i in range(0, len(data), 4096):
            self.m.update_status(
                "Sending Image to mBed: {:>02,.2%}".format(i/len(data)), 0)
            self.s.send(data[i:i+4096])
            recieved = self.s.recv(1024)
            print recieved
        self.m.update_status("Image Sent", 0)
        self.disconnect()
      except socket.error, msg:
        self.m.update_status("Failed to send Image", 0)
    os.remove('.temp')


class Vector:
  """Vectors for use in determining kinematics."""

  def __init__(self, position=(0,0,0)):
    self.data = tuple(position)
    if isinstance(position, Vector):
      self.data = position.data

  def __repr__(self):
    return repr(self.data)

  def __add__(self, a):
    return Vector([x[0] + x[1] for x in zip(self.data, a.data)])

  def __iadd__(self, a):
    return Vector([x[0] + x[1] for x in zip(self.data, a.data)])

  def __sub__(self, a):
    return Vector([x[0] - x[1] for x in zip(self.data, a.data)])

  def __isub__(self, a):
    return Vector([x[0] - x[1] for x in zip(self.data, a.data)])

  def __mul__(self, a):
    """Dot product."""
    if isinstance(a, Vector):
      return sum([x[0] * x[1] for x in zip(self.data, a.data)])
    return Vector([a * x for x in self.data])

  def __imul__(self, a):
    """Dot product."""
    if isinstance(a, Vector):
      return sum([x[0] * x[1] for x in zip(self.data, a.data)])
    return Vector([a * x for x in self.data])

  def __neg__(self):
    return Vector([-x for x in self.data])

  def cross(self, other):
    """Cross product."""
    a = self.data
    b = other.data
    i = a[1] * b[2] - a[2] * b[1]
    j = a[2] * b[0] - a[0] * b[2]
    k = a[0] * b[1] - a[1] * b[0]
    return Vector((i,j,k))

  def length(self):
    """Length of the vector"""
    dist = self.data[0]
    for i in self.data[1:]:
      dist = math.sqrt(dist * dist + i * i)
    return dist

  def longest(self):
    """The longest component of the vector."""
    return max([abs(x) for x in self.data])

  def normalize(self):
    """Change the value of the vector so its length is one."""
    dist = self.length()
    self.data = map((lambda x: x / dist), self.data)

  def normalized(self):
    """Return a new vector with a length of one."""
    dist = self.length()
    return Vector(map((lambda x: x / dist), self.data))

  def phi(self):
    """The angle of the vector on the x-y plane."""
    return math.atan2(self.data[1], self.data[0]) * 180 / math.pi

  def proj(self, other):
    """The projection of the other vector onto this vector."""
    return self *((self * other) / (self * self))

  def round(self):
    """Round all values to the nearest integer."""
    self.data = tuple([round(x) for x in self.data])

  def scale(self, length):
    """Scale the vector to the given length."""
    s = length/self.length()
    self.data = tuple([s * x for x in self.data])

  def theta(self):
    """The angle between -z and the vector."""
    return math.acos(self * Vector((0,0,-1)) / self.length()) * 180 / math.pi

  def tuple(self):
    return self.data

  def x(self):
    return self.data[0]

  def y(self):
    return self.data[1]

  def z(self):
    return self.data[2]


convert = Convert()