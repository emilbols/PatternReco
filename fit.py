import numpy as np
from numpy import genfromtxt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
data = genfromtxt('measurement_sensor002.csv', delimiter=',')
print(data)
edge = data[:,0]
x = data[:,1]/(1000.0*10.0)
dist = data[:,2]

Polynomial = np.polynomial.Polynomial
mean = np.mean(dist)
#select = np.logical_and( (dist[:] > mean-50.0), (dist[:] < mean+50) )
#print(mean)
#x = x[select]
#dist = dist[select]
#print(x)
xmin, xmax = np.amin(x), np.amax(x)
edges = [0,1,2,3]

for n in edges:
    selector = edge == n
    print(x[selector])
    print(dist[selector])
    pfit, stats = Polynomial.fit(x[selector], dist[selector], 1, full=True, window=(xmin, xmax), domain=(xmin,xmax)) 
    plt.plot(x[selector], dist[selector],'o', color='k')
    plt.plot(x[selector], pfit(x[selector]), color='r')
    axes = plt.gca()

    ymin, ymax = min(dist[selector])-30.0, max(dist[selector])+30.0

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
    fig.savefig('fit_sensor002_edge'+str(n)+'.png', dpi=100)
    plt.clf()
    #plt.show()
