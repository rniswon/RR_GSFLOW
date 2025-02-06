import numpy as np

def model(x):
    a = x[0]
    b = x[1]
    c = x[2]
    xx = np.arange(10, 30, 0.1)
    yy = a + b * np.power(xx, 3.5) - c * np.power(xx, 2.1)
    return yy


if __name__ == "__main__":
    
    #xx = np.arange(-10, 10, 0.1)
    # true system
    #par = np.array([1.5, 5, 2.33])
    fid = open('input.dat', 'r')
    par = fid.readlines()
    fid.close()
    par = [float(p) for p in par]
    par = np.array(par)
    yy = model(par)
    indx = [50, 95, 125, 130, 193]
    yo = yy[indx]

    fid = open('output.dat','w')
    for yyy in yo:
        fid.write(str(yyy))
        fid.write("\n")

    fid.close()
    pass
