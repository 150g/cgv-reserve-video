import db
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

db = db.DB(1)
coordinates = np.rot90(db.getSeat(), 3)
x,y,z = coordinates

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_trisurf(x, y, z)
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
plt.show()
