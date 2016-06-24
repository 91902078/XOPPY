import sys
import numpy
from PyQt4.QtGui import QIntValidator, QDoubleValidator, QApplication, QSizePolicy
from PyMca5.PyMcaIO import specfilewrapper as specfile
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets.widget import OWWidget
from oasys.widgets.exchange import DataExchangeObject
from orangewidget.widget import OWAction

from srxraylib.sources import srfunc
from orangecontrib.xoppy.util import xoppy_util

class OWbm(OWWidget):
    name = "bm"
    id = "orange.widgets.databm"
    description = "xoppy application to compute..."
    icon = "icons/xoppy_bm.png"
    author = "create_widget.py"
    maintainer_email = "srio@esrf.eu"
    priority = 7
    category = ""
    keywords = ["xoppy", "bm"]
    outputs = [{"name": "xoppy_data",
                "type": numpy.ndarray,
                "doc": ""},
               {"name": "xoppy_specfile",
                "type": str,
                "doc": ""},
               {"name": "xoppy_exchange_data",
               "type": DataExchangeObject,
               "doc": ""},]

    #inputs = [{"name": "Name",
    #           "type": type,
    #           "handler": None,
    #           "doc": ""}]

    want_main_area = False

    TYPE_CALC = Setting(0)
    MACHINE_NAME = Setting("ESRF bending magnet")
    RB_CHOICE = Setting(0)
    MACHINE_R_M = Setting(25.0)
    BFIELD_T = Setting(0.8)
    BEAM_ENERGY_GEV = Setting(6.0)
    CURRENT_A = Setting(0.1)
    HOR_DIV_MRAD = Setting(1.0)
    VER_DIV = Setting(0)
    PHOT_ENERGY_MIN = Setting(100.0)
    PHOT_ENERGY_MAX = Setting(100000.0)
    NPOINTS = Setting(500)
    LOG_CHOICE = Setting(1)
    PSI_MRAD_PLOT = Setting(1.0)
    PSI_MIN = Setting(-1.0)
    PSI_MAX = Setting(1.0)
    PSI_NPOINTS = Setting(500)


    def __init__(self):
        super().__init__()

        self.runaction = OWAction("Compute", self)
        self.runaction.triggered.connect(self.compute)
        self.addAction(self.runaction)

        box0 = gui.widgetBox(self.controlArea, "Input",orientation="horizontal")
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Compute", callback=self.compute)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.help1)
        self.process_showers()
        box = gui.widgetBox(self.controlArea, " ",orientation="vertical") 
        
        
        idx = -1 
        
        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "TYPE_CALC",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Energy or Power spectra', 'Angular distribution (all wavelengths)', 'Angular distribution (one wavelength)', '2D flux and power (angular,energy) distribution'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 1 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MACHINE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "RB_CHOICE",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Magnetic Radius', 'Magnetic Field'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 3 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MACHINE_R_M",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 4 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "BFIELD_T",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 5 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "BEAM_ENERGY_GEV",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 6 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "CURRENT_A",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 7 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "HOR_DIV_MRAD",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 8 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "VER_DIV",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Full (integrated in Psi)', 'At Psi=0', 'In [PsiMin,PsiMax]', 'At Psi=Psi_Min'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 9 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "PHOT_ENERGY_MIN",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 10 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "PHOT_ENERGY_MAX",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 11 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "NPOINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 12 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "LOG_CHOICE",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Lin', 'Log'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 13 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "PSI_MRAD_PLOT",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 14 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "PSI_MIN",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 15 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "PSI_MAX",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 16 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "PSI_NPOINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 

        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ['Type of calculation','Machine name','B from:','Machine Radius [m]','Magnetic Field [T]','Beam energy [GeV]','Beam Current [A]','Horizontal div Theta [mrad]','Psi (vertical div) for energy spectra','Min Photon Energy [eV]','Max Photon Energy [eV]','Number of energy points','Separation between energy points','Max Psi[mrad] for angular plots','Psi min [mrad]','Psi max [mrad]','Number of Psi points']


    def unitFlags(self):
         return ['True','True','True','self.RB_CHOICE  ==  0','self.RB_CHOICE  ==  1','True','True','True','True','True','True','True','True','True','self.VER_DIV  >=  2','self.VER_DIV  ==  2','self.VER_DIV  ==  2']


    #def unitNames(self):
    #     return ['TYPE_CALC','MACHINE_NAME','RB_CHOICE','MACHINE_R_M','BFIELD_T','BEAM_ENERGY_GEV','CURRENT_A','HOR_DIV_MRAD','VER_DIV','PHOT_ENERGY_MIN','PHOT_ENERGY_MAX','NPOINTS','LOG_CHOICE','PSI_MRAD_PLOT','PSI_MIN','PSI_MAX','PSI_NPOINTS']


    def compute(self):
        fileName = xoppy_calc_bm(TYPE_CALC=self.TYPE_CALC,MACHINE_NAME=self.MACHINE_NAME,RB_CHOICE=self.RB_CHOICE,MACHINE_R_M=self.MACHINE_R_M,BFIELD_T=self.BFIELD_T,BEAM_ENERGY_GEV=self.BEAM_ENERGY_GEV,CURRENT_A=self.CURRENT_A,HOR_DIV_MRAD=self.HOR_DIV_MRAD,VER_DIV=self.VER_DIV,PHOT_ENERGY_MIN=self.PHOT_ENERGY_MIN,PHOT_ENERGY_MAX=self.PHOT_ENERGY_MAX,NPOINTS=self.NPOINTS,LOG_CHOICE=self.LOG_CHOICE,PSI_MRAD_PLOT=self.PSI_MRAD_PLOT,PSI_MIN=self.PSI_MIN,PSI_MAX=self.PSI_MAX,PSI_NPOINTS=self.PSI_NPOINTS)
        #send specfile

        if fileName == None:
            print("Nothing to send")
        else:
            self.send("xoppy_specfile",fileName)
            sf = specfile.Specfile(fileName)
            if sf.scanno() == 1:
                #load spec file with one scan, # is comment
                print("Loading file:  ",fileName)
                out = numpy.loadtxt(fileName)
                print("data shape: ",out.shape)
                #get labels
                txt = open(fileName).readlines()
                tmp = [ line.find("#L") for line in txt]
                itmp = numpy.where(numpy.array(tmp) != (-1))
                labels = txt[itmp[0]].replace("#L ","").split("  ")
                print("data labels: ",labels)
                self.send("xoppy_data",out)

                exchange_data = DataExchangeObject("XOPPY", "BM")

                exchange_data.add_content("xoppy_specfile", fileName)
                exchange_data.add_content("xoppy_data", out)
                exchange_data.add_content("is_log_plot", self.LOG_CHOICE)

                self.send("xoppy_exchange_data", exchange_data)
            else:
                print("File %s contains %d scans. Cannot send it as xoppy_table"%(fileName,sf.scanno()))

    def defaults(self):
         self.resetSettings()
         self.compute()
         return

    def help1(self):
        xoppy_util.xoppy_doc('bm')


def xoppy_calc_bm(MACHINE_NAME="ESRF bending magnet",RB_CHOICE=0,MACHINE_R_M=25.0,BFIELD_T=0.8,\
                  BEAM_ENERGY_GEV=6.04,CURRENT_A=0.1,HOR_DIV_MRAD=1.0,VER_DIV=0,\
                  PHOT_ENERGY_MIN=100.0,PHOT_ENERGY_MAX=100000.0,NPOINTS=500,LOG_CHOICE=1,\
                  PSI_MRAD_PLOT=1.0,PSI_MIN=-1.0,PSI_MAX=1.0,PSI_NPOINTS=500,TYPE_CALC=0):
    print("Inside xoppy_calc_bm. ")

    outFile = "bm.spec"

    # electron energy in GeV
    gamma = BEAM_ENERGY_GEV*1e3 / srfunc.codata_mee

    r_m = MACHINE_R_M      # magnetic radius in m
    if RB_CHOICE == 1:
        r_m = srfunc.codata_me * srfunc.codata_c / srfunc.codata_ec / BFIELD_T * numpy.sqrt(gamma * gamma - 1)

    # calculate critical energy in eV
    ec_m = 4.0*numpy.pi*r_m/3.0/numpy.power(gamma,3) # wavelength in m
    ec_ev = srfunc.m2ev / ec_m


    if TYPE_CALC == 0:
        if LOG_CHOICE == 0:
            energy_ev = numpy.linspace(PHOT_ENERGY_MIN,PHOT_ENERGY_MAX,NPOINTS) # photon energy grid
        else:
            energy_ev = numpy.logspace(numpy.log10(PHOT_ENERGY_MIN),numpy.log10(PHOT_ENERGY_MAX),NPOINTS) # photon energy grid

        a5 = srfunc.sync_ene(VER_DIV, energy_ev, ec_ev=ec_ev, polarization=0, \
                             e_gev=BEAM_ENERGY_GEV, i_a=CURRENT_A, hdiv_mrad=HOR_DIV_MRAD, \
                             psi_min=PSI_MIN, psi_max=PSI_MAX, psi_npoints=PSI_NPOINTS)

        a5par = srfunc.sync_ene(VER_DIV, energy_ev, ec_ev=ec_ev, polarization=1, \
                                e_gev=BEAM_ENERGY_GEV, i_a=CURRENT_A, hdiv_mrad=HOR_DIV_MRAD, \
                                psi_min=PSI_MIN, psi_max=PSI_MAX, psi_npoints=PSI_NPOINTS)

        a5per = srfunc.sync_ene(VER_DIV, energy_ev, ec_ev=ec_ev, polarization=2, \
                                e_gev=BEAM_ENERGY_GEV, i_a=CURRENT_A, hdiv_mrad=HOR_DIV_MRAD, \
                                psi_min=PSI_MIN, psi_max=PSI_MAX, psi_npoints=PSI_NPOINTS)

        if VER_DIV == 0:
            coltitles=['Photon Energy [eV]','Photon Wavelength [A]','E/Ec','Flux_spol/Flux_total','Flux_ppol/Flux_total','Flux[Phot/sec/0.1%bw]','Power[Watts/eV]']
            title='integrated in Psi,'
        if VER_DIV == 1:
            coltitles=['Photon Energy [eV]','Photon Wavelength [A]','E/Ec','Flux_spol/Flux_total','Flux_ppol/Flux_total','Flux[Phot/sec/0.1%bw/mradPsi]','Power[Watts/eV/mradPsi]']
            title='at Psi=0,'
        if VER_DIV == 2:
            coltitles=['Photon Energy [eV]','Photon Wavelength [A]','E/Ec','Flux_spol/Flux_total','Flux_ppol/Flux_total','Flux[Phot/sec/0.1%bw]','Power[Watts/eV]']
            title='in Psi=[%e,%e]'%(PSI_MIN,PSI_MAX)

        if VER_DIV == 3:
            coltitles=['Photon Energy [eV]','Photon Wavelength [A]','E/Ec','Flux_spol/Flux_total','Flux_ppol/Flux_total','Flux[Phot/sec/0.1%bw/mradPsi]','Power[Watts/eV/mradPsi]']
            title='at Psi=%e mrad'%(PSI_MIN)

        a6=numpy.zeros((7,len(energy_ev)))
        a1 = energy_ev
        a6[0,:] = (a1)
        a6[1,:] = srfunc.m2ev * 1e10 / (a1)
        a6[2,:] = (a1)/ec_ev # E/Ec
        a6[3,:] = (a5par)/(a5)
        a6[4,:] = (a5per)/(a5)
        a6[5,:] = (a5)
        a6[6,:] = (a5)*1e3 * srfunc.codata_ec

    if TYPE_CALC == 1:  # angular distributions over over all energies
        angle_mrad = numpy.linspace(-PSI_MRAD_PLOT, +PSI_MRAD_PLOT,NPOINTS) # angle grid

        a6 = numpy.zeros((6,NPOINTS))
        a6[0,:] = angle_mrad # angle in mrad
        a6[1,:] = angle_mrad*gamma/1e3 # Psi[rad]*Gamma
        a6[2,:] = srfunc.sync_f(angle_mrad * gamma / 1e3)
        a6[3,:] = srfunc.sync_f(angle_mrad * gamma / 1e3, polarization=1)
        a6[4,:] = srfunc.sync_f(angle_mrad * gamma / 1e3, polarization=2)
        a6[5,:] = srfunc.sync_ang(0, angle_mrad, i_a=CURRENT_A, hdiv_mrad=HOR_DIV_MRAD, e_gev=BEAM_ENERGY_GEV, r_m=r_m)

        coltitles=['Psi[mrad]','Psi[rad]*Gamma','F','F s-pol','F p-pol','Power[Watts/mrad(Psi)]']

    if TYPE_CALC == 2:  # angular distributions at a single energy
        angle_mrad = numpy.linspace(-PSI_MRAD_PLOT, +PSI_MRAD_PLOT,NPOINTS) # angle grid

        a6 = numpy.zeros((7,NPOINTS))
        a6[0,:] = angle_mrad # angle in mrad
        a6[1,:] = angle_mrad*gamma/1e3 # Psi[rad]*Gamma
        a6[2,:] = srfunc.sync_f(angle_mrad * gamma / 1e3)
        a6[3,:] = srfunc.sync_f(angle_mrad * gamma / 1e3, polarization=1)
        a6[4,:] = srfunc.sync_f(angle_mrad * gamma / 1e3, polarization=2)
        tmp = srfunc.sync_ang(1, angle_mrad, energy=PHOT_ENERGY_MIN, i_a=CURRENT_A, hdiv_mrad=HOR_DIV_MRAD, e_gev=BEAM_ENERGY_GEV, ec_ev=ec_ev)
        tmp.shape = -1
        a6[5,:] = tmp
        a6[6,:] = a6[5,:] * srfunc.codata_ec * 1e3

        coltitles=['Psi[mrad]','Psi[rad]*Gamma','F','F s-pol','F p-pol','Flux[Ph/sec/0.1%bw/mradPsi]','Power[Watts/eV/mradPsi]']


    if TYPE_CALC == 3:  # angular,energy distributions flux
        angle_mrad = numpy.linspace(-PSI_MRAD_PLOT, +PSI_MRAD_PLOT,NPOINTS) # angle grid

        if LOG_CHOICE == 0:
            energy_ev = numpy.linspace(PHOT_ENERGY_MIN,PHOT_ENERGY_MAX,NPOINTS) # photon energy grid
        else:
            energy_ev = numpy.logspace(numpy.log10(PHOT_ENERGY_MIN),numpy.log10(PHOT_ENERGY_MAX),NPOINTS) # photon energy grid

        tmp1, fm, a = srfunc.sync_ene(2, energy_ev, ec_ev=ec_ev, e_gev=BEAM_ENERGY_GEV, i_a=CURRENT_A, \
                                      hdiv_mrad=HOR_DIV_MRAD, psi_min=PSI_MIN, psi_max=PSI_MAX, psi_npoints=PSI_NPOINTS)

        a6 = numpy.zeros((4,len(a)*len(energy_ev)))
        ij = -1
        for i in range(len(a)):
            for j in range(len(energy_ev)):
                ij += 1
                a6[0,ij] = a[i]
                a6[1,ij] = energy_ev[j]
                a6[2,ij] = fm[i,j] * srfunc.codata_ec * 1e3
                a6[3,ij] = fm[i,j]

        coltitles=['Psi [mrad]','Photon Energy [eV]','Power [Watts/eV/mradPsi]','Flux [Ph/sec/0.1%bw/mradPsi]']

        import matplotlib.pylab as plt
        from mpl_toolkits.mplot3d import Axes3D  # need for example 6

        toptitle='Flux vs vertical angle and photon energy'
        xtitle  ='angle [mrad]'
        ytitle  ='energy [eV]'
        ztitle = "Photon flux [Ph/s/mrad/0.1%bw]"
        pltN = 0
        fig = plt.figure(pltN)
        ax = fig.add_subplot(111, projection='3d')
        fa, fe = numpy.meshgrid(a, energy_ev)
        surf = ax.plot_surface(fa, fe, fm.T, \
            rstride=1, cstride=1, \
            linewidth=0, antialiased=False)

        plt.title(toptitle)
        ax.set_xlabel(xtitle)
        ax.set_ylabel(ytitle)
        ax.set_zlabel(ztitle)
        plt.show()

    # write spec file
    ncol = len(coltitles)
    npoints = len(a6[0,:])

    f = open(outFile,"w")
    f.write("#F "+outFile+"\n")
    f.write("\n")
    f.write("#S 1 bm results\n")
    f.write("#N %d\n"%(ncol))
    f.write("#L")
    for i in range(ncol):
        f.write("  "+coltitles[i])
    f.write("\n")

    for i in range(npoints):
            f.write((" %e "*ncol+"\n")%(tuple(a6[:,i].tolist())))
    f.close()
    print("File written to disk: " + outFile)

    return outFile




if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWbm()
    w.show()
    app.exec()
    w.saveSettings()