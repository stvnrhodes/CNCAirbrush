X_STEP_INCH = 1
Y_STEP_INCH = 1
Z_STEP_INCH = 1
PAN_INT_ANGLE = 360 / 1024
TILT_INT_ANGLE = 90 / 1024
import math
import socket

class Convert:

  def int_to_angle(cls, int, axis='pan'):
    return int * factor(axis)

  def angle_to_int(cls, angle, axis='pan'):
    return round(angle / factor(axis))

  def step_to_unit(cls, step, unit='in', axis='x'):
    return step * _get_factor(axis, unit)
    
  def unit_to_step(cls, num, unit='in', axis='x'):
    return round(num / _get_factor(axis, unit))
    
  def _get_factor(cls, axis, unit='in'):
    if axis == 'x':
      factor = X_STEP_INCH
    elif axis == 'y':
      factor = Y_STEP_INCH
    elif axis == 'z':
      factor = Z_STEP_INCH
    elif axis == 'pan':
      factor = PAN_INT_ANGLE
    elif axis == 'tilt':
      factor = TILT_INT_ANGLE
    if unit == 'mil':
      factor *= 1000
    elif unit == 'mm':
      factor *= 25.4
    return factor
 
 
class Machine:
  """The class that will send data to the machine."""

  def __init__(self, *args, **kargs):
    self.com = Communicate()
  
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
    self.base = p2 - p1
    self.height = p3 - p1
    self.height -= self.base.proj(self.height)
    self.normal = self.base.cross(self.height)
    if self.normal.theta() > 90:
      self.normal = -self.normal
    
  def set_bitmap(self, pic):
    self.pic = pic

  def get_size(self):
    """Returns the size in steps of the picture."""
    return (self.base.longest(), self.height.longest())
    
  def jog(self, axis, num, unit = 'step'):
    """Moves num units in axis direction"""
    if unit != 'step':
      num = Convert.unit_to_step(num)
    if axis == 'x':
      self._move_rel((num, 0, 0))
    elif axis == 'y':
      self._move_rel((0, num, 0))
    elif axis == 'z':
      self._move_rel((0, 0, num))
  
  def _change_angle(self, angles):
    """Send angle change command to machine"""
    angles = [Convert.angleToInt(x) for x in angles]
    self.com.send('g03 ' + ' '.join([str(x) for x in location]))
  
  def _move_rel(self, location):
    """Send relative movement command to machine"""
    location = [round(x) for x in location]
    self.com.send('g00 ' + ' '.join([str(x) for x in location]))
  
  def _get_img_data(self):
    return self.pic.resize(get_size()).convert('1')
  
  
class Communicate:
  """This class handles the low-level communication details."""
  
  def send(self, msg):
    """Send the message to the machine"""
  
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