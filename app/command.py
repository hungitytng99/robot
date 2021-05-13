from enum import Enum

class Command(Enum):
  DRIVE      = 1
  TURN_LEFT  = 2
  TURN_RIGHT = 3
  REVERSE    = 4
  GRAB       = 5
  UNGRAB     = 6
  STOP       = 7

  def __str__(self):
      return self.name

  def __repr__(self):
      return self.name

