X_STEP_INCH = 1
Y_STEP_INCH = 1
Z_STEP_INCH = 1
PAN_INT_ANGLE = 360 / 1024
TILT_INT_ANGLE = 90 / 1024
STEPS_PER_PIXEL = 3
FEED_RATE = 100 # in steps/s
HOST = '169.254.1.1'
PORT = 2000

import math
import socket
import binascii
import os


class Convert:

  def int_to_angle(cls, int, axis='pan'):
    return int * cls._get_factor(axis)

  def angle_to_int(cls, angle, axis='pan'):
    return round(angle / cls._get_factor(axis))

  def step_to_unit(cls, step, unit='in', axis='x'):
    return step * cls._get_factor(axis, unit)

  def unit_to_step(cls, num, unit='in', axis='x'):
    return round(num / cls._get_factor(axis, unit))

  def _get_factor(cls, axis, unit='in'):
    if axis in 'xX':
      factor = X_STEP_INCH
    elif axis in 'yY':
      factor = Y_STEP_INCH
    elif axis in 'zZ':
      factor = Z_STEP_INCH
    elif axis == 'pan':
      factor = PAN_INT_ANGLE
    elif axis == 'tilt':
      factor = TILT_INT_ANGLE
    if unit == 'mil':
      factor *= 1000
    elif unit == 'mm':
      factor *= 25.4
    elif unit == 'step':
      factor = 1
    return factor


convert = Convert()


class Machine:
  """The class that will send data to the machine."""

  def __init__(self, *args, **kargs):
    self.update_status = lambda x, y: None
    self.com = Communicate(self)
    self.p1 = None
    self.p2 = None
    self.p3 = None
    self.base = None
    self.height = None
    self.normal = None
    self.units = 'in'

  def set_points(self, p1=None, p2=None, p3=None):
    """Set the points for the machine.
    p1 and p2 determine the base, p3 determines the height
    """
    if p1 != None:
      self.p1 = Vector(self._tuple_to_step(p1))
    if p2 != None:
      self.p2 = Vector(self._tuple_to_step(p2))
    if p3 != None:
      self.p3 = Vector(self._tuple_to_step(p3))
    if self._plane_points_defined():
      self.base = self.p2 - self.p1
      self.height = self.p3 - self.p1
      if self.height.length() != 0:
        self.height -= self.base.proj(self.height)
        self.normal = self.base.cross(self.height)
        if self.normal.theta() > 90:
          self.normal = -self.normal
        print "Size: " + str(self.base) + ", " + str(self.height)
      else:
        self.height = None

  def _plane_points_defined(self):
    return self.p1 and self.p2 and self.p3

  def all_points_defined(self):
    return self.base and self.height

  def set_units(self, units):
    """Change the units to a new type"""
    self.units = units

  def set_status_function(self, f):
    """Set the function that allows you to change the status bar"""
    self.update_status = f

  def set_bitmap(self, pic):
    self.pic = pic

  def get_longest_side_size(self):
    """Returns the size in steps of the picture."""
    return (self.base.longest(), self.height.longest())

  def get_position(self):
    """Queries the machine for the current position of X, Y Z, Pan, and Tilt"""


  def jog(self, axis, num, unit = 'step'):
    """Moves num units in axis direction"""
    if axis in 'xX':
      num = convert.unit_to_step(num, unit, axis)
      self._move_rel((num, 0, 0))
    elif axis in 'yY':
      num = convert.unit_to_step(num, unit, axis)
      self._move_rel((0, num, 0))
    elif axis in 'zZ':
      num = convert.unit_to_step(num, unit, axis)
      self._move_rel((0, 0, num))

  def _change_angle(self, angles):
    """Send angle change command to machine"""
    angles = [convert.angleToInt(x) for x in angles]
    self.com.send('g03 ' + ' '.join([str(x) for x in location]))

  def _move_rel(self, location):
    """Send relative movement command to machine"""
    location = [round(x) for x in location]
    self.com.send('g00 ' + ' '.join([str(x) for x in location]))

  def _get_img_data(self):
    return self.pic.resize(get_size()).convert('1')

  def _tuple_to_step(self, tuple):
    return (convert.unit_to_step(tuple[0], self.units, 'x'),
            convert.unit_to_step(tuple[1], self.units, 'y'),
            convert.unit_to_step(tuple[2], self.units, 'z'))


class Communicate:
  """This class handles the low-level communication details."""

  def __init__(self, machine):
    self.m = machine
    self.connect()

  def connect(self):
    """Attempt to connect to the WiFly"""
    try:
      self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.s.connect((HOST, PORT))
      self.connected = True
      self.m.update_status("Connected to mBed", 1)
    except socket.error, msg:
      self.connected = False
      self.s.close()
      self.m.update_status("No Communication", 1)

  def disconnect(self):
    self.s.close()
    self.connected = False
      
  def send(self, msg):
    """Send the message to the machine"""
    if not self.connected:
      self.connect()
    try:
      self.m.update_status("Sending to mBed: " + str(msg), 0)
      self.s.send(msg)
      self.m.update_status("Sent to mBed: " + str(msg), 0)
      self.m.update_status("Connected to mBed", 1)
      self.disconnect()
    except socket.error, msg:
      self.connect()

  def send_image(self, img):
    """Send the image to the machine, ASCII encoded in base 16"""
    img.convert('1').save('.temp', 'bmp')
    if not self.connected:
      self.connect()
    try:
      self.m.update_status("Sending Image to mBed", 0)
      with open('.temp', 'rb') as f:
        self.s.send(binascii.hexlify(f.read()))
      os.remove('.temp')
      self.m.update_status("Image Sent", 0)   
      self.disconnect()      
    except socket.error, msg:
      self.connect()
    

  def get_data(self):
    """Retrieve relevant data from the machine"""


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
    self.data = tuple([-x for x in self.data])

  def tuple(self):
    return self.data

  def x(self):
    return self.data[0]

  def y(self):
    return self.data[1]

  def z(self):
    return self.data[2]

  def normalize(self):
    """Change the value of the vector so its length is one."""
    dist = self.length()
    self.data = map((lambda x: x / dist), self.data)

  def normalized(self):
    """Return a new vector with a length of one."""
    dist = self.length()
    return Vector(map((lambda x: x / dist), self.data))

  def cross(self, other):
    """Cross product."""
    a = self.data
    b = other.data
    i = a[1] * b[2] - a[2] * b[1]
    j = a[2] * b[0] - a[0] * b[2]
    k = a[0] * b[1] - a[1] * b[0]
    return Vector((i,j,k))

  def phi(self):
    """The angle of the vector on the x-y plane."""
    return math.atan2(self.data[1], self.data[0]) * 180 / math.pi

  def theta(self):
    """The angle between -z and the vector."""
    return math.acos(self * Vector((0,0,-1)) / self._length()) * 180 / math.pi

  def proj(self, other):
    """The projection of the other vector onto this vector."""
    return self *((self * other) / (self * self))

  def length(self):
    """Length of the vector"""
    dist = self.data[0]
    for i in self.data[1:]:
      dist = math.sqrt(dist * dist + i * i)
    return dist

  def scale(self, length):
    """Scale the vector to the given length."""
    s = length/self.length()
    self.data = tuple([s * x for x in self.data])

  def round(self):
    """Round all values to the nearest integer."""
    self.data = tuple([round(x) for x in self.data])

  def longest(self):
    """The longest component of the vector."""
    return max([abs(x) for x in self.data])