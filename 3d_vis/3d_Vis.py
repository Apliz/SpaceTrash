from csv import reader
def makecubelimits(axis, centers=None, hw=None):
    lims = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
    if centers == None:
        centers = [0.5*sum(pair) for pair in lims]

    if hw == None:
        widths  = [pair[1] - pair[0] for pair in lims]
        hw      = 0.5*max(widths)
        ax.set_xlim(centers[0]-hw, centers[0]+hw, auto=True)
        ax.set_ylim(centers[1]-hw, centers[1]+hw, auto=True)
        ax.set_zlim(centers[2]-hw, centers[2]+hw, auto=True)
        print("hw was None so set to:", hw)
    else:
        try:
            hwx, hwy, hwz = hw
            print("ok hw requested: ", hwx, hwy, hwz)

            ax.set_xlim(centers[0]-hwx, centers[0]+hwx)
            ax.set_ylim(centers[1]-hwy, centers[1]+hwy)
            ax.set_zlim(centers[2]-hwz, centers[2]+hwz)
        except:
            print("nope hw requested: ", hw)
            ax.set_xlim(centers[0]-hw, centers[0]+hw)
            ax.set_ylim(centers[1]-hw, centers[1]+hw)
            ax.set_zlim(centers[2]-hw, centers[2]+hw)

    return centers, hw


from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
import mpld3 as mpld3
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from csv import DictReader

halfpi, pi, twopi = [f*np.pi for f in (0.5, 1, 2)]
degs, rads = 180/pi, pi/180

load = Loader('~/Documents/fishing/SkyData')
data = load('de421.bsp')
ts   = load.timescale()

satellites = []

planets = load('de421.bsp')
earth   = planets['earth']


hours = np.arange(0, 3, 0.01)

time = ts.utc(2018, 2, 7, hours)

def orbit(TLE):
    L1 = row['TLE_LINE1']
    L2 = row['TLE_LINE2']
    Roadster = EarthSatellite(L1, L2)
    print(Roadster.epoch.tt)
    return Roadster.at(time).position.km

re = 6378.

theta = np.linspace(0, twopi, 201)
cth, sth, zth = [f(theta) for f in (np.cos, np.sin, np.zeros_like)]
lon0 = re*np.vstack((cth, zth, sth))
lons = []
for phi in rads*np.arange(0, 180, 15):
    cph, sph = [f(phi) for f in (np.cos, np.sin)]
    lon = np.vstack((lon0[0]*cph - lon0[1]*sph,
                     lon0[1]*cph + lon0[0]*sph,
                     lon0[2]) )
    lons.append(lon)

lat0 = re*np.vstack((cth, sth, zth))
lats = []
for phi in rads*np.arange(-75, 90, 15):
    cph, sph = [f(phi) for f in (np.cos, np.sin)]
    lat = re*np.vstack((cth*cph, sth*cph, zth+sph))
    lats.append(lat)


# open file in read mode
with open('../API/TLE_data.csv', 'r') as TLE_Data:
    # pass the file object to reader() to get the reader object
    TLE_List = DictReader(TLE_Data)
# Iterate over each row in the csv using reader object
    for row in TLE_List:
        # row variable is a list that represents a row in csv
        satellites.append(orbit(row))


if True:
    fig = plt.figure(figsize=[10, 8])  # [12, 10]

    ax  = fig.add_subplot(1, 1, 1, projection='3d')

    for Rpos in satellites:

        print(Rpos.shape)
        x, y, z = Rpos
        ax.plot(x, y, z)
        for x, y, z in lons:
            ax.plot(x, y, z, '-k')
        for x, y, z in lats:
            ax.plot(x, y, z, '-k')

        centers, hw = makecubelimits(ax)

        print("centers are: ", centers)
        print("hw is:       ", hw)
mpld3.fig_to_html(fig, no_extras=False, template_type='simple')
mpld3.save_html(fig, 'spacegraph.html')
mpld3.save_json(fig, 'spacegraph-alt.html')
plt.show()
