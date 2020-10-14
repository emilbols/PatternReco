import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
data = genfromtxt('measurement.csv', delimiter=' ')
x = data[:,0]/(1000.0*10.0)
dist = data[:,1]
Polynomial = np.polynomial.Polynomial
mean = np.mean(dist)
select = np.logical_and( (dist[:] > mean-50.0), (dist[:] < mean+50) )
print(mean)
x = x[select]
dist = dist[select]
xmin, xmax = min(x), max(x)
ymin, ymax = min(dist)-10.0, max(dist)+10.0

pfit, stats = Polynomial.fit(x, dist, 1, full=True, window=(xmin, xmax), domain=(xmin,xmax))

plt.plot(x, dist,'o', color='k')
plt.plot(x, pfit(x), color='r')
axes = plt.gca()
axes.set_ylim([ymin,ymax])
plt.xlabel('module lenght [$\mathrm{cm}]$')
plt.ylabel('mask to edge distance [$\mathrm{\mu m}$]')
#shift_str = "max dist = " + str(pfit(10.0)-pfit(0)) + " $\mu \mathrm{m}$ " 
angle = round(( ( pfit(10.0)-pfit(0) )/ ( 0.1 * 1000.0 * 1000.0 ) )*1000.0*1000.0 , 2)
angle_str = "angle = " + str(angle) + " $\mu \mathrm{rad}$"

#plt.text(xmin+2, ymin+4, shift_str, fontsize=12)
plt.text(xmin+1, ymin+20, angle_str, fontsize=12)

fig = plt.gcf()
fig.set_size_inches(10.5, 10.5)
fig.savefig('fit.png', dpi=100)
#plt.show()
