import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import ones, zeros

grid = None

def draw_grid():
	# This assumes you are using a numpy array for your grid
	width, height = grid.shape
	glRasterPos2f(-1, -1)
	glDrawPixels(width, height, GL_LUMINANCE, GL_FLOAT, grid)
	glFlush()
	glutSwapBuffers()

def update_grid(new_grid):
	global grid

	rGrid = ones((800,800))
	
	#for y in range(len(new_grid)-1,-1,-1):
	for x in range(0,len(new_grid[0])):
		for y in range(0,len(new_grid)):
			#rGrid[y][len(new_grid)-x-1] = new_grid[x][y]
			rGrid[x][y] = new_grid[y][len(new_grid)-x-1]
			#rGrid[len(new_grid)-x-1] = new_grid[x][::-1]

	grid2 = ones((800,800))
	for x in range(0,len(new_grid[0])):
		for y in range(0,len(new_grid)):
			#rGrid[y][len(new_grid)-x-1] = new_grid[x][y]
			grid2[x][y] = rGrid[y][len(new_grid)-x-1]

	grid = grid2
	#grid = rGrid

def init_window(width, height):
	global window
	global grid
	grid = zeros((width, height))
	glutInit(())
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowSize(width, height)
	glutInitWindowPosition(0, 0)
	window = glutCreateWindow("Grid filter")
	glutDisplayFunc(draw_grid)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluOrtho2D(-1,1,-1,1)
	glViewport(0,0,800,800)
	#glutMainLoop()
