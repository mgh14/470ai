from __future__ import division
from itertools import cycle

try:
    from numpy import linspace
except ImportError:
    # This is stolen from numpy.  If numpy is installed, you don't
    # need this:
    def linspace(start, stop, num=50, endpoint=True, retstep=False):
        """Return evenly spaced numbers.

        Return num evenly spaced samples from start to stop.  If
        endpoint is True, the last sample is stop. If retstep is
        True then return the step value used.
        """
        num = int(num)
        if num <= 0:
            return []
        if endpoint:
            if num == 1:
                return [float(start)]
            step = (stop-start)/float((num-1))
            y = [x * step + start for x in xrange(0, num - 1)]
            y.append(stop)
        else:
            step = (stop-start)/float(num)
            y = [x * step + start for x in xrange(0, num)]
        if retstep:
            return y, step
        else:
            return y

WORLDSIZE = 800
SAMPLES = 30
VEC_LEN = 0.75 * WORLDSIZE / SAMPLES

class GnuplotUtil(object):

	@staticmethod
	def gnuplot_header(minimum, maximum):
		'''Return a string that has all of the gnuplot sets and unsets.'''
		s = ''
		s += 'set xrange [%s: %s]\n' % (minimum, maximum)
		s += 'set yrange [%s: %s]\n' % (minimum, maximum)
		# The key is just clutter.  Get rid of it:
		s += 'unset key\n'
		# Make sure the figure is square since the world is square:
		s += 'set size square\n'
		# Add a pretty title (optional):
		#s += "set title 'Potential Fields'\n"
		return s
	
	@staticmethod
	def draw_line(p1, p2):
		'''Return a string to tell Gnuplot to draw a line from point p1 to
		point p2 in the form of a set command.'''
		x1, y1 = p1
		x2, y2 = p2
		return 'set arrow from %s, %s to %s, %s nohead lt 3\n' % (x1, y1, x2, y2)

	@staticmethod
	def plot_field(fieldX,fieldY):
		'''Return a Gnuplot command to plot a field.'''
		s = "plot '-' with vectors head\n"

		separation = WORLDSIZE / SAMPLES
		end = WORLDSIZE / 2 - separation / 2
		start = -end

		points = ((x, y) for x in linspace(start, end, SAMPLES)
			for y in linspace(start, end, SAMPLES))

		for x, y in points:
			f_x = fieldX[int(x)][int(y)]
			f_y = fieldY[int(x)][int(y)]
			plotvalues = GnuplotUtil.gpi_point(x, y, f_x, f_y)
			if plotvalues is not None:
				x1, y1, x2, y2 = plotvalues
				s += '%s %s %s %s\n' % (x1, y1, x2, y2)
		s += 'e\n'
		
		return s

	@staticmethod
	def gpi_point(x, y, vec_x, vec_y):
		'''Create the centered gpi data point (4-tuple) for a position and
		vector.  The vectors are expected to be less than 1 in magnitude,
		and larger values will be scaled down.'''
		r = (vec_x ** 2 + vec_y ** 2) ** 0.5
		if r > 1:  # normalize the vector if magnitude is > 1
			vec_x /= r
			vec_y /= r
		return (x - vec_x * VEC_LEN / 2, y - vec_y * VEC_LEN / 2,
			vec_x * VEC_LEN, vec_y * VEC_LEN)

	@staticmethod
	def draw_obstacles(obstacles):
		'''Return a string which tells Gnuplot to draw all of the obstacles.'''
		s = 'unset arrow\n'

		for obs in obstacles:
			last_point = obs[0]
		for cur_point in obs[1:]:
			s += draw_line(last_point, cur_point)
			last_point = cur_point
			s += draw_line(last_point, obs[0])
		return s
	
