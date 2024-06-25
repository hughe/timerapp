# Experiment with the App API.
#
# https://github.com/pi-top/pi-top-4-Miniscreen/blob/master/pt_miniscreen/core/README.md
import time

from pt_miniscreen.core import App
from pt_miniscreen.core import Component
from pt_miniscreen.core.components.marquee_text import MarqueeText

from pitop.miniscreen import Miniscreen

class Timer(Component):
  # define a `default_state` dictionary to create state with known values
  default_state = {
    "started": 0,
    "now": None,
    "stopped": None,
    "running": False
  }

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.text = self.create_child(
      MarqueeText,
      text="Push Select to Start",
      font_size=10,
      align="center",
      vertical_align="center",
    )
    self._tick_interval = None

  def select_button_pressed(self):
    now = time.time()
    if not self.state["running"]:
      # Staring the clock
      self.state.update(started=now,
                        stopped=None,
                        now=now,
                        running=True)
      assert self._tick_interval is None
      self._tick_interval = self.create_interval(self.tick, timeout=1)
    else:
      # Stopping the clock
      self.state.update(stopped=now,
                        now=now,
                        running=False)
      self.remove_interval(self._tick_interval)
      self._tick_interval = None
    self.update_text()

  def tick(self):
    now = time.time()
    assert self.state["running"]
    self.state.update(now=now)
    self.update_text()

  def update_text(self):
    t = None
    if self.state["running"]:
      t = "------Running------\n{0:2.2f}s".format(self.state["now"] - self.state["started"])
    elif not self.state["running"] and self.state["stopped"] is not None:
      t = "------Stopped------\n{0:2.2f}\nSelect to Restart".format(self.state["stopped"] - self.state["started"])
    else:
      t = "Push Select to Start"
      
    self.text.state.update(text=t)
    
  def render(self, image):
    return self.text.render(image)
    
class TimerApp(App):
  def __init__(self, miniscreen):
    super().__init__(display=miniscreen.device.display, Root=Timer)

    # We call methods on self, because self.root does not exist until
    # start() is run. So if we said `self.root.button_pressed` we'd
    # get an exception.
    miniscreen.select_button.when_pressed = self.select_button_pressed
    miniscreen.cancel_button.when_pressed = self.cancel_button_pressed

  def select_button_pressed(self):
    self.root.select_button_pressed()

  def cancel_button_pressed(self):
    self.stop()

def main():
  m = Miniscreen()

  a = TimerApp(m)
  
  a.start()
  a.wait_for_stop()

if __name__ == '__main__':
  main()
