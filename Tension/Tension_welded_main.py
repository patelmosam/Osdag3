from .tension_welded_ui import Ui_MainWindow
from .ui_design_preferences import Ui_DesignPreferences
from .ui_design_summary import Ui_DesignReport

from .svg_window import SvgWindow
from ui_tutorial import Ui_Tutorial
from ui_aboutosdag import Ui_AboutOsdag
from ui_ask_question import Ui_AskQuestion
from .Tension_calc import tension_welded_design
from .drawing2D_tension_weld import Tension_drawing
from .reportGenerator import save_html
from OCC.Display.backend import load_backend, get_qt_modules
# from drawing_2D import ExtendedEndPlate
# from OCC.Core.Graphic3d import Graphic3d_NOT_2D_ALUMINUM


from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFontDialog, QFileDialog
from PyQt5.Qt import QColor, QBrush, Qt, QIntValidator, QDoubleValidator, QFile, QTextStream, pyqtSignal, QColorDialog, \
    QPixmap, QPalette
from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from .model import *
import sys
import os
import pickle
import pdfkit
import json
import configparser
import cairosvg
import shutil
import subprocess

# from Connections.Component.ISection import ISection
# from Connections.Component.nut import Nut
# from Connections.Component.bolt import Bolt
from Connections.Component.filletweld import FilletWeld
# from Connections.Component.groove_weld import GrooveWeld
# from Connections.Component.stiffener_plate import StiffenerPlate
from Connections.Component.plate import Plate
from Connections.Component.angle import Angle
from Connections.Component.channel import Channel

from .cadFile import CAD \
 \
from Connections.Component.quarterCone import QuarterCone
from OCC.Core.Quantity import Quantity_NOC_SADDLEBROWN
from OCC.Core import IGESControl, BRepTools
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs

from utilities import osdag_display_shape
import copy


class MyTutorials(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_Tutorial()
        self.ui.setupUi(self)
        self.mainController = parent


class MyAskQuestion(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_AskQuestion()
        self.ui.setupUi(self)
        self.mainController = parent


class MyAboutOsdag(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_AboutOsdag()
        self.ui.setupUi(self)
        self.mainController = parent


class DesignPreference(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_DesignPreferences()
        self.ui.setupUi(self)
        self.maincontroller = parent

        self.saved = None
        self.ui.combo_design_method.model().item(1).setEnabled(False)
        self.ui.combo_design_method.model().item(2).setEnabled(False)
        self.save_default_para()
        dbl_validator = QDoubleValidator()
        self.ui.txt_boltFu.setValidator(dbl_validator)
        self.ui.txt_boltFu.setMaxLength(7)
        self.ui.txt_weldFu.setValidator(dbl_validator)
        self.ui.txt_weldFu.setMaxLength(7)
        self.ui.btn_defaults.clicked.connect(self.save_default_para)
        # self.ui.btn_save.clicked.connect(self.save_designPref_para)
        self.ui.btn_save.hide()
        self.ui.btn_close.clicked.connect(self.close_designPref)

    # self.ui.combo_boltHoleType.currentIndexChanged[str].connect(self.get_clearance)

    def save_designPref_para(self):
        uiObj = self.maincontroller.get_user_inputs()
        self.saved_designPref = {}
        # self.saved_designPref["bolt"] = {}
        # self.saved_designPref["bolt"]["bolt_type"] = str(self.ui.combo_boltType.currentText())
        # self.saved_designPref["bolt"]["bolt_hole_type"] = str(self.ui.combo_boltHoleType.currentText())
        # self.saved_designPref["bolt"]["bolt_hole_clrnce"] = self.get_clearance()
        # self.saved_designPref["bolt"]["bolt_fu"] = float(str(self.ui.txt_boltFu.text()))
        # self.saved_designPref["bolt"]["slip_factor"] = float(str(self.ui.combo_slipfactor.currentText()))

        self.saved_designPref["weld"] = {}
        weldType = str(self.ui.combo_weldType.currentText())
        self.saved_designPref["weld"]["typeof_weld"] = weldType
        if weldType == "Shop weld":
            self.saved_designPref["weld"]["safety_factor"] = float(1.25)
        else:
            self.saved_designPref["weld"]["safety_factor"] = float(1.5)
        self.saved_designPref["weld"]["fu_overwrite"] = self.ui.txt_weldFu.text()

        self.saved_designPref["detailing"] = {}
        typeOfEdge = str(self.ui.combo_detailingEdgeType.currentText())
        self.saved_designPref["detailing"]["typeof_edge"] = typeOfEdge
        if typeOfEdge == "a - Sheared or hand flame cut":
            self.saved_designPref["detailing"]["min_edgend_dist"] = float(1.7)
        else:
            self.saved_designPref["detailing"]["min_edgend_dist"] = float(1.5)

        self.saved_designPref["detailing"]["is_env_corrosive"] = str(self.ui.combo_detailing_memebers.currentText())
        self.saved_designPref["design"] = {}
        self.saved_designPref["design"]["design_method"] = str(self.ui.combo_design_method.currentText())
        self.saved = True

        # QMessageBox.about(self, 'Information', "Preferences saved")

        return self.saved_designPref

    def save_default_para(self):
        uiObj = self.maincontroller.get_user_inputs()
        # if uiObj["Bolt"]["Grade"] == '':
        # 	pass
        # else:
        # 	bolt_grade = float(uiObj["Bolt"]["Grade"])
        # 	bolt_fu = str(self.get_boltFu(bolt_grade))
        # 	self.ui.txt_boltFu.setText(bolt_fu)
        self.ui.combo_boltType.setCurrentIndex(1)
        self.ui.combo_boltHoleType.setCurrentIndex(0)
        designPref = {}
        # designPref["bolt"] = {}
        # designPref["bolt"]["bolt_type"] = str(self.ui.combo_boltType.currentText())
        # designPref["bolt"]["bolt_hole_type"] = str(self.ui.combo_boltHoleType.currentText())
        # designPref["bolt"]["bolt_hole_clrnce"] = self.get_clearance()
        # designPref["bolt"]["bolt_fu"] = float(self.ui.txt_boltFu.text())
        # self.ui.combo_slipfactor.setCurrentIndex(4)
        # designPref["bolt"]["slip_factor"] = float(str(self.ui.combo_slipfactor.currentText()))

        self.ui.combo_weldType.setCurrentIndex(0)
        designPref["weld"] = {}
        weldType = str(self.ui.combo_weldType.currentText())
        designPref["weld"]["typeof_weld"] = weldType
        designPref["weld"]["safety_factor"] = float(1.25)
        Fu = str(uiObj["Member"]["fu (MPa)"])
        self.ui.txt_weldFu.setText(Fu)
        designPref["weld"]["fu_overwrite"] = self.ui.txt_weldFu.text()
        self.ui.combo_detailingEdgeType.setCurrentIndex(0)
        designPref["detailing"] = {}
        typeOfEdge = str(self.ui.combo_detailingEdgeType.currentText())
        designPref["detailing"]["typeof_edge"] = typeOfEdge
        designPref["detailing"]["min_edgend_dist"] = float(1.7)
        self.ui.combo_detailing_memebers.setCurrentIndex(0)
        designPref["detailing"]["is_env_corrosive"] = str(self.ui.combo_detailing_memebers.currentText())

        designPref["design"] = {}
        designPref["design"]["design_method"] = str(self.ui.combo_design_method.currentText())
        self.saved = False
        return designPref

    def set_weldFu(self):
        """
		Returns: Set weld Fu based on member fu
		"""
        uiObj = self.maincontroller.get_user_inputs()
        Fu = str(uiObj["Member"]["fu (MPa)"])
        self.ui.txt_weldFu.setText(Fu)

    def set_boltFu(self):
        uiObj = self.maincontroller.get_user_inputs()
        boltGrade = str(uiObj["Bolt"]["Grade"])
        if boltGrade != '':
            boltfu = str(self.get_boltFu(boltGrade))
            self.ui.txt_boltFu.setText(boltfu)
        else:
            pass

    # def get_clearance(self):
    #
    # 	uiObj = self.maincontroller.get_user_inputs()
    # 	boltDia = str(uiObj["Bolt"]["Diameter (mm)"])
    # 	if boltDia != 'Select diameter':
    #
    # 		standard_clrnce = {12: 1, 14: 1, 16: 2, 18: 2, 20: 2, 22: 2, 24: 2, 30: 3, 34: 3, 36: 3}
    # 		overhead_clrnce = {12: 3, 14: 3, 16: 4, 18: 4, 20: 4, 22: 4, 24: 6, 30: 8, 34: 8, 36: 8}
    # 		boltHoleType = str(self.ui.combo_boltHoleType.currentText())
    # 		if boltHoleType == "Standard":
    # 			clearance = standard_clrnce[int(boltDia)]
    # 		else:
    # 			clearance = overhead_clrnce[int(boltDia)]
    #
    # 		return clearance
    # 	else:
    # 		pass

    def get_boltFu(self, boltGrade):
        """
		Args:
			boltGrade: Friction Grip Bolt or Bearing Bolt
		Returns: ultimate strength of bolt depending upon grade of bolt chosen
		"""
        # boltFu = {3.6: 330, 4.6: 400, 4.8: 420, 5.6: 500, 5.8: 520, 6.8: 600, 8.8: 800, 9.8: 900, 10.9: 1040,
        # 		  12.9: 1220}
        boltGrd = float(boltGrade)
        boltFu = int(boltGrd) * 100  # Nominal strength of bolt
        return boltFu

    def close_designPref(self):
        self.close()

    def closeEvent(self, QCloseEvent):
        self.save_designPref_para()
        QCloseEvent.accept()


class DesignReportDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_DesignReport()
        self.ui.setupUi(self)
        self.maincontroller = parent
        self.setWindowTitle("Design Profile")
        self.ui.btn_browse.clicked.connect(lambda: self.getLogoFilePath(self.ui.lbl_browse))
        self.ui.btn_saveProfile.clicked.connect(self.saveUserProfile)
        self.ui.btn_useProfile.clicked.connect(self.useUserProfile)
        self.accepted.connect(self.save_inputSummary)

    def save_inputSummary(self):
        report_summary = self.get_report_summary()
        self.maincontroller.save_design(report_summary)

    def getLogoFilePath(self, lblwidget):
        self.ui.lbl_browse.clear()
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', "../../ ", 'Images (*.png *.svg *.jpg)', None,
                                                  QFileDialog.DontUseNativeDialog)
        flag = True
        if filename == '':
            flag = False
            return flag
        else:
            base = os.path.basename(str(filename))
            lblwidget.setText(base)
            base_type = base[-4:]
            self.desired_location(filename, base_type)

        return str(filename)

    def desired_location(self, filename, base_type):
        if base_type == ".svg":
            cairosvg.svg2png(file_obj=filename, write_to=os.path.join(str(self.maincontroller.folder), "images_html",
                                                                      "cmpylogoExtendEndplate.svg"))
        else:
            shutil.copyfile(filename,
                            os.path.join(str(self.maincontroller.folder), "images_html", "cmpylogoExtendEndplate.png"))

    def saveUserProfile(self):
        inputData = self.get_report_summary()
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Files',
                                                  os.path.join(str(self.maincontroller.folder), "Profile"), '*.txt')
        if filename == '':
            flag = False
            return flag
        else:
            with open(filename, 'w') as infile:
                json.dump(inputData, infile)

    def get_report_summary(self):
        report_summary = {"ProfileSummary": {}}
        report_summary["ProfileSummary"]["CompanyName"] = str(self.ui.lineEdit_companyName.text())
        report_summary["ProfileSummary"]["CompanyLogo"] = str(self.ui.lbl_browse.text())
        report_summary["ProfileSummary"]["Group/TeamName"] = str(self.ui.lineEdit_groupName.text())
        report_summary["ProfileSummary"]["Designer"] = str(self.ui.lineEdit_designer.text())

        report_summary["ProjectTitle"] = str(self.ui.lineEdit_projectTitle.text())
        report_summary["Subtitle"] = str(self.ui.lineEdit_subtitle.text())
        report_summary["JobNumber"] = str(self.ui.lineEdit_jobNumber.text())
        report_summary["Client"] = str(self.ui.lineEdit_client.text())
        report_summary["AdditionalComments"] = str(self.ui.txt_additionalComments.toPlainText())

        return report_summary

    def useUserProfile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Files',
                                                  os.path.join(str(self.maincontroller.folder), "Profile"),
                                                  "All Files (*)")
        if os.path.isfile(filename):
            with open(filename, 'r') as outfile:
                reportsummary = json.load(outfile)
            self.ui.lineEdit_companyName.setText(reportsummary["ProfileSummary"]['CompanyName'])
            self.ui.lbl_browse.setText(reportsummary["ProfileSummary"]['CompanyLogo'])
            self.ui.lineEdit_groupName.setText(reportsummary["ProfileSummary"]['Group/TeamName'])
            self.ui.lineEdit_designer.setText(reportsummary["ProfileSummary"]['Designer'])
        else:
            pass


class Maincontroller(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, folder):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()
        self.folder = folder
        self.connection = "Tension"
        self.get_sectiondata(self)
        # self.get_beamdata()
        self.result_obj = None
        # self.endplate_type = ''
        self.designPrefDialog = DesignPreference(self)
        # self.ui.combo_connLoc.model().item(1).setEnabled(False)
        # self.ui.combo_connLoc.model().item(2).setEnabled(False)
        # self.ui.combo_connLoc.currentIndexChanged.connect(self.get_beamdata)
        # self.ui.combo_beamSec.setCurrentIndex(0)

        # import math
        # beam_section = self.fetchBeamPara()
        # t_w = float(beam_section["tw"])
        # t_f = float(beam_section["T"])
        # print t_w, t_f
        # t_thicker = math.ceil(max(t_w, t_f))
        # t_thicker = (t_thicker / 2.) * 2
        #
        # self.plate_thickness = {'Select plate thickness':[t_thicker, t_thicker+2]}

        self.gradeType = {'Please select type': '', 'Friction Grip Bolt': [8.8, 10.9],
                          'Bearing Bolt': [3.6, 4.6, 4.8, 5.6, 5.8, 6.8, 8.8, 9.8, 10.9, 12.9]}
        # self.ui.combo_type.addItems(self.gradeType.keys())
        # self.ui.combo_type.currentIndexChanged[str].connect(self.combotype_current_index_changed)
        # self.ui.combo_type.setCurrentIndex(0)
        self.retrieve_prevstate()
        # self.ui.combo_connLoc.currentIndexChanged[str].connect(self.setimage_connection)

        self.ui.btnFront.clicked.connect(lambda: self.call_2D_drawing("Front"))
        self.ui.btnTop.clicked.connect(lambda: self.call_2D_drawing("Top"))
        self.ui.btnSide.clicked.connect(lambda: self.call_2D_drawing("Side"))
        # self.ui.combo_diameter.currentIndexChanged[str].connect(self.bolt_hole_clearance)
        # self.ui.combo_grade.currentIndexChanged[str].connect(self.call_bolt_fu)
        self.ui.txt_Fu.textChanged.connect(self.call_weld_fu)
        # added
        self.ui.combo_sectiontype.currentTextChanged.connect(self.get_sectiondata)
        # self.ui.combo_sectiontype.currentTextChanged.connect(self.Typechanged)
        ##########
        self.ui.btn_Design.clicked.connect(self.design_btnclicked)
        self.ui.btn_Design.clicked.connect(self.osdag_header)
        self.ui.btn_Design.clicked.connect(self.image1)
        self.ui.btn_Design.clicked.connect(self.image2)
        self.ui.btn_Design.clicked.connect(self.image3)
        self.ui.btn_Design.clicked.connect(self.image4)
        self.ui.btn_Reset.clicked.connect(self.reset_btnclicked)
        self.ui.btnInput.clicked.connect(lambda: self.dockbtn_clicked(self.ui.inputDock))
        self.ui.btnOutput.clicked.connect(lambda: self.dockbtn_clicked(self.ui.outputDock))
        self.ui.actionDesign_Preferences.triggered.connect(self.design_prefer)
        self.ui.actionEnlarge_font_size.triggered.connect(self.show_font_dialogue)
        self.ui.action_save_input.triggered.connect(self.save_design_inputs)
        self.ui.action_load_input.triggered.connect(self.load_design_inputs)
        self.ui.actionSave_log_messages.triggered.connect(self.save_log_messages)
        # self.ui.actionSave_3D_model.triggered.connect(self.save_3D_cad_images)
        self.ui.actionCreate_design_report.triggered.connect(self.design_report)
        # self.ui.actionChange_background.triggered.connect(self.show_color_dialog)
        self.ui.actionSave_Front_View.triggered.connect(lambda: self.call_2D_drawing("Front"))
        self.ui.actionSave_Side_View.triggered.connect(lambda: self.call_2D_drawing("Side"))
        self.ui.actionSave_Top_View.triggered.connect(lambda: self.call_2D_drawing("Top"))
        self.ui.actionShow_all.triggered.connect(lambda: self.call_3DModel("gradient_bg"))
        self.ui.actionShow_column.triggered.connect(lambda: self.call_3DColumn("gradient_bg"))
        self.ui.actionShow_beam.triggered.connect(lambda: self.call_3DBeam("gradient_bg"))
        self.ui.actionShow_connector.triggered.connect(lambda: self.call_3DConnector("gradient_bg"))
        self.ui.actionSave_current_image.triggered.connect(self.save_CAD_images)
        self.ui.actionZoom_in.triggered.connect(self.call_zoomin)
        self.ui.actionZoom_out.triggered.connect(self.call_zoomout)
        self.ui.actionPan.triggered.connect(self.call_pannig)
        self.ui.actionRotate_3D_model.triggered.connect(self.call_rotation)
        self.ui.actionClear.triggered.connect(self.clear_log_messages)
        self.ui.actionAbout_Osdag_2.triggered.connect(self.open_about_osdag)
        self.ui.actionAsk_Us_a_Question.triggered.connect(self.open_ask_question)
        self.ui.actionSample_Tutorials.triggered.connect(self.open_tutorials)
        self.ui.actionDesign_examples.triggered.connect(self.design_examples)
        # self.ui.combo_conn_loc.currentTextChanged.connect(self.conn_on_change)
        # self.ui.combo_sectiontype.currentTextChanged.connect(self.type_on_change)
        # self.ui.combo_conn_loc.activated.connect(self.on_change)
        # self.ui.btn_Weld.clicked.connect(self.weld_details)
        # self.ui.btn_pitchDetail.clicked.connect(self.pitch_details)
        # self.ui.btn_plateDetail.clicked.connect(self.plate_details)
        # self.ui.btn_plateDetail_2.clicked.connect(self.plate_details_bottom)
        # self.ui.btn_stiffnrDetail.clicked.connect(self.stiffener_details)
        self.ui.btn_CreateDesign.clicked.connect(self.design_report)
        self.ui.btn_SaveMessages.clicked.connect(self.save_log_messages)

        self.ui.btn3D.clicked.connect(lambda: self.call_3DModel("gradient_bg"))
        # self.ui.chkBx_columnSec.clicked.connect(lambda: self.call_3DColumn("gradient_bg"))
        # self.ui.chkBx_beamSec.clicked.connect(lambda: self.call_3DBeam("gradient_bg"))
        # self.ui.chkBx_connector.clicked.connect(lambda: self.call_3DConnector("gradient_bg"))

        validator = QIntValidator()

        doubl_validator = QDoubleValidator()
        self.ui.txt_Fu.setValidator(doubl_validator)
        self.ui.txt_Fy.setValidator(doubl_validator)
        self.ui.txt_Tensionforce.setValidator(doubl_validator)
        self.ui.txt_Member_length.setValidator(doubl_validator)
        self.ui.txt_Tensionforce.setValidator(doubl_validator)

        min_fu = 290
        max_fu = 780
        self.ui.txt_Fu.editingFinished.connect(lambda: self.check_range(self.ui.txt_Fu, min_fu, max_fu))
        self.ui.txt_Fu.editingFinished.connect(
            lambda: self.validate_fu_fy(self.ui.txt_Fu, self.ui.txt_Fy, self.ui.txt_Fu, self.ui.lbl_fu))

        min_fy = 165
        max_fy = 650
        self.ui.txt_Fy.editingFinished.connect(lambda: self.check_range(self.ui.txt_Fy, min_fy, max_fy))
        self.ui.txt_Fy.editingFinished.connect(
            lambda: self.validate_fu_fy(self.ui.txt_Fu, self.ui.txt_Fy, self.ui.txt_Fy, self.ui.lbl_fy))

        # TODO #

        self.ui.txt_oppline_tension.editingFinished.connect(
            lambda: self.check_weld_range(self.ui.txt_oppline_tension, self.ui.lbl_beam1_3, self.uiObj))
        # TODO #

        from osdagMainSettings import backend_name
        self.display, _ = self.init_display(backend_str=backend_name())
        self.uiObj = None
        self.fuse_model = None
        self.resultObj = None
        self.disable_buttons()

    def init_display(self, backend_str=None, size=(1024, 768)):

        used_backend = load_backend(backend_str)
        global display, start_display, app, _, USED_BACKEND
        if 'qt' in used_backend:
            from OCC.Display.qtDisplay import qtViewer3d
            QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()

        from OCC.Display.qtDisplay import qtViewer3d
        self.ui.modelTab = qtViewer3d(self)

        # ========================  CAD ========================
        self.ui.mytabWidget.resize(size[0], size[1])
        self.ui.mytabWidget.addTab(self.ui.modelTab, "")
        self.ui.modelTab.InitDriver()
        # ===========================================================
        display = self.ui.modelTab._display
        display.set_bg_gradient_color([23, 1, 32], [23, 1, 32])
        # ========================  CAD ========================
        display.display_triedron()
        # ===========================================================
        display.View.SetProj(1, 1, 1)

        def centerOnScreen(self):
            '''Centers the window on the screen.'''
            resolution = QtGui.QDesktopWidget().screenGeometry()
            self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                      (resolution.height() / 2) - (self.frameSize().height() / 2))

        def start_display():
            self.ui.modelTab.raise_()

        return display, start_display

    def save_design_inputs(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Design", os.path.join(str(self.folder), "untitled.osi"),
                                                  "Input Files osi(*.osi)")
        if not filename:
            return
        try:
            out_file = open(str(filename), 'wb')
        except IOError:
            QMessageBox.information(self, "Unable to open file",
                                    "There was an error opening \"%s\"" % filename)
            return
        json.dump(self.uiObj, out_file)
        out_file.close()
        pass

    def load_design_inputs(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Design", str(self.folder), "osi(*.osi)")
        if not filename:
            return
        try:
            in_file = open(str(filename), 'rb')
        except IOError:
            QMessageBox.information(self, "Unable to open file",
                                    "There was an error opening \"%s\"" % filename)
            return
        ui_obj = json.load(in_file)
        self.set_dict_touser_inputs(ui_obj)

    def save_log_messages(self):
        filename, pat = QFileDialog.getSaveFileName(self, "Save File As", os.path.join(str(self.folder), "LogMessages"),
                                                    "Text files (*.txt)")
        return self.save_file(filename + ".txt")

    def save_file(self, filename):
        """
		Args:
			filename: file name
		Returns: open file for writing
		"""
        fname = QFile(filename)
        if not fname.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "Application",
                                "Cannot write file %s:\n%s." % (filename, fname.errorString()))
            return
        outf = QTextStream(fname)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        outf << self.ui.textEdit.toPlainText()
        QApplication.restoreOverrideCursor()

    def save_design(self, report_summary):
        status = self.resultObj['Tension_Force']['Design_Status']
        if status is True:
            self.call_3DModel("white_bg")
            data = os.path.join(str(self.folder), "images_html", "3D_Model.png")
            self.display.ExportToImage(data)
            self.display.FitAll()
        else:
            pass

        filename = os.path.join(str(self.folder), "images_html", "Html_Report.html")
        file_name = str(filename)
        self.call_designreport(file_name, report_summary)

        # Creates PDF
        config = configparser.ConfigParser()
        config.readfp(open(r'Osdag.config'))
        wkhtmltopdf_path = config.get('wkhtml_path', 'path1')

        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        options = {
            'margin-bottom': '10mm',
            'footer-right': '[page]'
        }
        file_type = "PDF(*.pdf)"
        fname, _ = QFileDialog.getSaveFileName(self, "Save File As", self.folder + "/", file_type)
        fname = str(fname)
        flag = True
        if fname == '':
            flag = False
            return flag
        else:
            pdfkit.from_file(filename, fname, configuration=config, options=options)
            QMessageBox.about(self, 'Information', "Report Saved")

    def call_designreport(self, fileName, report_summary):
        self.alist = self.designParameters()
        self.result = tension_welded_design(self.alist)
        print("resultobj", self.result)
        self.column_data = self.fetchColumnPara()
        self.beam_data = self.fetchBeamPara()
        save_html(self.result, self.alist, self.column_data, self.beam_data, fileName, report_summary, self.folder)

    def get_user_inputs(self):
        uiObj = {}
        uiObj["Member"] = {}
        uiObj["Member"]["Location"] = str(self.ui.combo_conn_loc.currentText())
        uiObj["Member"]["SectionType"] = str(self.ui.combo_sectiontype.currentText())
        uiObj["Member"]["SectionSize"] = str(self.ui.combo_sectionsize.currentText())
        uiObj["Member"]["fu (MPa)"] = self.ui.txt_Fu.text()
        uiObj["Member"]["fy (MPa)"] = self.ui.txt_Fy.text()
        uiObj["Member"]["Member_length"] = self.ui.txt_Member_length.text()

        uiObj["Load"] = {}
        uiObj["Load"]["AxialForce (kN)"] = self.ui.txt_Tensionforce.text()

        uiObj["Weld"] = {}
        uiObj["Weld"]["inline_tension"] = self.ui.txt_inline_tension.text()
        uiObj["Weld"]["oppline_tension"] = self.ui.txt_oppline_tension.text()
        uiObj["Weld"]["Platethickness"] = self.ui.txt_plate_thk.text()

        uiObj["Support_Condition"] = {}
        uiObj["Support_Condition"]["end1_cond1"] = self.ui.combo_end1_cond1.currentText()
        uiObj["Support_Condition"]["end1_cond2"] = self.ui.combo_end1_cond2.currentText()
        uiObj["Support_Condition"]["end2_cond1"] = self.ui.combo_end2_cond1.currentText()
        uiObj["Support_Condition"]["end2_cond2"] = self.ui.combo_end2_cond2.currentText()
        uiObj["Connection"] = self.connection

        return uiObj

    def osdag_header(self):
        image_path = os.path.abspath(os.path.join(os.getcwd(), os.path.join("ResourceFiles", "Osdag_header.png")))
        shutil.copyfile(image_path, os.path.join(str(self.folder), "images_html", "Osdag_header.png"))

    def image1(self):
        image_path = os.path.abspath(os.path.join(os.getcwd(),
                                                  os.path.join("Connections/Moment/BCEndPlate/ResourceFiles/images",
                                                               "Butt_weld_double_flange.png")))
        shutil.copyfile(image_path, os.path.join(str(self.folder), "images_html", "Butt_weld_double_flange.png"))

    def image2(self):
        image_path = os.path.abspath(os.path.join(os.getcwd(),
                                                  os.path.join("Connections/Moment/BCEndPlate/ResourceFiles/images",
                                                               "Butt_weld_double_web.png")))
        shutil.copyfile(image_path, os.path.join(str(self.folder), "images_html", "Butt_weld_double_web.png"))

    def image3(self):
        image_path = os.path.abspath(os.path.join(os.getcwd(),
                                                  os.path.join("Connections/Moment/BCEndPlate/ResourceFiles/images",
                                                               "Butt_weld_single_web.png")))
        shutil.copyfile(image_path, os.path.join(str(self.folder), "images_html", "Butt_weld_single_web.png"))

    def image4(self):
        image_path = os.path.abspath(os.path.join(os.getcwd(),
                                                  os.path.join("Connections/Moment/BCEndPlate/ResourceFiles/images",
                                                               "Butt_weld_single_flange.png")))
        shutil.copyfile(image_path, os.path.join(str(self.folder), "images_html", "Butt_weld_single_flange.png"))

    def design_prefer(self):
        self.designPrefDialog.show()

    def bolt_hole_clearance(self):
        self.designPrefDialog.get_clearance()

    def call_bolt_fu(self):
        self.designPrefDialog.set_boltFu()

    def call_weld_fu(self):
        self.designPrefDialog.set_weldFu()

    def closeEvent(self, event):
        """
		Args:
			event: Yes or No
		Returns: Ask for the confirmation while closing the window
		"""
        uiInput = self.designParameters()
        self.save_inputs_totext(uiInput)
        action = QMessageBox.question(self, "Message", "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        if action == QMessageBox.Yes:
            self.closed.emit()
            event.accept()
        else:
            event.ignore()

    def save_inputs_totext(self, uiObj):
        """
		Args:
			uiObj: User inputs
		Returns: Save the user input to txt format
		"""
        inputFile = os.path.join("Tension", "WsaveINPUT.txt")
        try:
            with open(inputFile, 'w') as input_file:
                json.dump(uiObj, input_file)
        except Exception as e:
            QMessageBox.warning(self, "Application",
                                "Cannot write file %s:\n%s" % (inputFile, str(e)))

    def get_prevstate(self):
        """
		Returns: Read for the previous user inputs design
		"""
        filename = os.path.join("Tension", "saveINPUT.txt")
        if os.path.isfile(filename):
            with open(filename, 'r') as file_object:
                uiObj = json.load(file_object)
            return uiObj
        else:
            return None

    def retrieve_prevstate(self):
        """
		Returns: Retrieve the previous user inputs
		"""
        uiObj = self.get_prevstate()
        self.set_dict_touser_inputs(uiObj)

    def set_dict_touser_inputs(self, uiObj):
        """
		Args:
			uiObj: User inputs
		Returns: Set the dictionary to user inputs
		"""

        if uiObj is not None:
            if uiObj["Connection"] != "Tension":
                QMessageBox.information(self, "Information",
                                        "You can load this input file only from the corresponding design problem")
                return

            self.ui.combo_conn_loc.setCurrentIndex(self.ui.combo_conn_loc.findText(uiObj["Member"]["Location"]))
            self.ui.combo_sectiontype.setCurrentIndex(
                self.ui.combo_sectiontype.findText(uiObj["Member"]["SectionType"]))
            self.ui.combo_sectionsize.setCurrentIndex(
                self.ui.combo_sectionsize.findText(uiObj["Member"]["SectionSize"]))
            self.ui.txt_Fu.setText(str(uiObj["Member"]["fu (MPa)"]))
            self.ui.txt_Fy.setText(str(uiObj["Member"]["fy (MPa)"]))
            self.ui.txt_Member_length.setText(str(uiObj["Member"]["Member_length"]))
            self.ui.txt_Tensionforce.setText(str(uiObj["Load"]["AxialForce (kN)"]))
            self.ui.txt_Member_length.setText(str(uiObj["Member"]["Member_length"]))
            self.ui.txt_plate_thk.setText(str(uiObj["Weld"]["Platethickness"]))
            self.ui.txt_inline_tension.setText(str(uiObj["Weld"]["inline_tension"]))
            self.ui.txt_oppline_tension.setText(str(uiObj["Weld"]["oppline_tension"]))
            self.ui.combo_end1_cond1.setCurrentIndex(
                self.ui.combo_end1_cond1.findText(uiObj["Support_Condition"]["end1_cond1"]))
            self.ui.combo_end1_cond2.setCurrentIndex(
                self.ui.combo_end1_cond1.findText(uiObj["Support_Condition"]["end1_cond2"]))
            self.ui.combo_end2_cond1.setCurrentIndex(
                self.ui.combo_end1_cond1.findText(uiObj["Support_Condition"]["end2_cond1"]))
            self.ui.combo_end2_cond2.setCurrentIndex(
                self.ui.combo_end1_cond1.findText(uiObj["Support_Condition"]["end2_cond2"]))
            self.designPrefDialog.ui.combo_weldType.setCurrentIndex(
                self.designPrefDialog.ui.combo_weldType.findText(uiObj["weld"]["typeof_weld"]))
            self.designPrefDialog.ui.txt_weldFu.setText(str(uiObj["weld"]["fu_overwrite"]))
            self.designPrefDialog.ui.combo_detailingEdgeType.setCurrentIndex(
                self.designPrefDialog.ui.combo_detailingEdgeType.findText(uiObj["detailing"]["typeof_edge"]))
            self.designPrefDialog.ui.combo_detailing_memebers.setCurrentIndex(
                self.designPrefDialog.ui.combo_detailing_memebers.findText(uiObj["detailing"]["is_env_corrosive"]))
            self.designPrefDialog.ui.combo_design_method.setCurrentIndex(
                self.designPrefDialog.ui.combo_design_method.findText(uiObj["design"]["design_method"]))

    def designParameters(self):
        """
		Returns: Design preference inputs
		"""
        self.uiObj = self.get_user_inputs()
        if self.designPrefDialog.saved is not True:
            design_pref = self.designPrefDialog.save_default_para()
        else:
            design_pref = self.designPrefDialog.save_designPref_para()
            self.uiObj.update(design_pref)
        return self.uiObj

    # def setimage_connection(self):
    # 	'''
    # 	Setting image to connectivity.
    # 	'''
    # 	self.ui.lbl_connectivity.show()
    # 	loc = self.ui.combo_connLoc.currentText()
    # 	loc2 = self.ui.combo_connect.currentText()
    #
    # 	if loc == "Extended both ways" and loc2 == "Column flange-Beam web":
    # 		pixmap = QPixmap(":/newPrefix/images/webextnboth.png")
    # 		pixmap.scaledToHeight(60)
    # 		pixmap.scaledToWidth(50)
    # 		self.ui.lbl_connectivity.setPixmap(pixmap)
    # 	elif loc == "Flush end plate" and loc2 == "Column flange-Beam web":
    # 		pixmap = QPixmap(":/newPrefix/images/webflush.png")
    # 		pixmap.scaledToHeight(60)
    # 		pixmap.scaledToWidth(50)
    # 		self.ui.lbl_connectivity.setPixmap(pixmap)
    # 	elif loc == "Extended one way" and loc2 == "Column flange-Beam web":
    # 		pixmap = QPixmap(":/newPrefix/images/webextnone.png")
    # 		pixmap.scaledToHeight(60)
    # 		pixmap.scaledToWidth(50)
    # 		self.ui.lbl_connectivity.setPixmap(pixmap)
    # 	elif loc == "Extended both ways" and loc2 == "Column web-Beam web":
    # 		pixmap = QPixmap(":/newPrefix/images/fextnboth.png")
    # 		pixmap.scaledToHeight(60)
    # 		pixmap.scaledToWidth(50)
    # 		self.ui.lbl_connectivity.setPixmap(pixmap)
    # 	elif loc == "Flush end plate" and loc2 == "Column web-Beam web":
    # 		pixmap = QPixmap(":/newPrefix/images/ff.png")
    # 		pixmap.scaledToHeight(60)
    # 		pixmap.scaledToWidth(50)
    # 		self.ui.lbl_connectivity.setPixmap(pixmap)
    # 	else:
    # 		pixmap = QPixmap(":/newPrefix/images/fextnone.png")
    # 		pixmap.scaledToHeight(60)
    # 		pixmap.scaledToWidth(50)
    # 		self.ui.lbl_connectivity.setPixmap(pixmap)
    #
    # 	return True

    def generate_incomplete_string(self, incomplete_list):
        """
		Args:
			incomplete_list: list of fields that are not selected or entered
		Returns:
			error string that has to be displayed
		"""

        # The base string which should be displayed
        information = "Please input the following required field"
        if len(incomplete_list) > 1:
            # Adds 's' to the above sentence if there are multiple missing input fields
            information += "s"
        information += ": "

        # Loops through the list of the missing fields and adds each field to the above sentence with a comma
        for item in incomplete_list:
            information = information + item + ", "

        # Removes the last comma
        information = information[:-2]
        information += "."

        return information

    def validate_inputs_on_design_btn(self):
        flag = True
        incomplete_list = []

        if self.ui.combo_conn_loc.currentIndex() == 0:
            incomplete_list.append("Location")

        if self.ui.combo_sectiontype.currentIndex() == 0:
            incomplete_list.append("Section Type")

        if self.ui.combo_sectionsize.currentIndex() == 0:
            incomplete_list.append("Section Size")

        if self.ui.txt_Fu.text() == "":
            incomplete_list.append("Ultimate strength")

        if self.ui.txt_Fy.text() == "":
            incomplete_list.append("Yield strength")

        if self.ui.txt_Member_length.text() == "":
            incomplete_list.append("Member length")

        if self.ui.txt_Tensionforce.text() == '' or float(self.ui.txt_Tensionforce.text()) == 0:
            incomplete_list.append("Axial force")

        # if self.ui.combo_conn_loc.currentText() == "Back to Back Angles":
        if self.ui.txt_plate_thk.text() == "":
            incomplete_list.append("Platethickness")
        # elif self.ui.combo_conn_loc.currentText() == "Star Angles":
        # 	if self.ui.txt_plate_thk.text() == "":
        # 		incomplete_list.append("Platethickness")
        # elif self.ui.combo_conn_loc.currentText() == "Back to Back Web":
        # 	if self.ui.txt_plate_thk.text() == "":
        # 		incomplete_list.append("Platethickness")
        # else:
        # 	pass

        if self.ui.txt_inline_tension.text() == "":
            incomplete_list.append("inline_tension")

        if self.ui.txt_oppline_tension.text() == "":
            incomplete_list.append("oppline_tension")

        if self.ui.combo_end1_cond1.currentIndex() == 0:
            incomplete_list.append("End 1 Condition 1")

        if self.ui.combo_end1_cond2.currentIndex() == 0:
            incomplete_list.append("End 1 Condition 2")

        if self.ui.combo_end2_cond1.currentIndex() == 0:
            incomplete_list.append("End 2 Condition 1")

        if self.ui.combo_end2_cond2.currentIndex() == 0:
            incomplete_list.append("End 2 Condition 2")

        if len(incomplete_list) > 0:
            flag = False
            QMessageBox.information(self, "Information", self.generate_incomplete_string(incomplete_list))

        return flag

    def wrong_combo(self):
        flag = True

        if self.ui.combo_conn_loc.currentText() == "Back to Back Angles" and self.ui.combo_sectiontype.currentText() != "Angles":
            flag = False
            QMessageBox.information(self, "Information", "Wrong Combination of Connection Type and Section Type")

        elif self.ui.combo_conn_loc.currentText() == "Star Angles" and self.ui.combo_sectiontype.currentText() != "Angles":
            flag = False
            QMessageBox.information(self, "Information", "Wrong Combination of Connection Type and Section Type")

        elif self.ui.combo_conn_loc.currentText() == "Leg" and self.ui.combo_sectiontype.currentText() != "Angles":
            flag = False
            QMessageBox.information(self, "Information", "Wrong Combination of Connection Type and Section Type")

        elif self.ui.combo_conn_loc.currentText() == "Back to Back Web" and self.ui.combo_sectiontype.currentText() != "Channels":
            flag = False
            QMessageBox.information(self, "Information", "Wrong Combination of Connection Type and Section Type")

        elif self.ui.combo_conn_loc.currentText() == "Flange" and self.ui.combo_sectiontype.currentText() == "Angles":
            flag = False
            QMessageBox.information(self, "Information", "Wrong Combination of Connection Type and Section Type")

        elif self.ui.combo_conn_loc.currentText() == "Web" and self.ui.combo_sectiontype.currentText() == "Angles":
            flag = False
            QMessageBox.information(self, "Information", "Wrong Combination of Connection Type and Section Type")

        else:
            flag = True

        return flag

    def design_btnclicked(self):
        """
		Returns:
		"""
        if self.wrong_combo() is not True:
            return
        if self.validate_inputs_on_design_btn() is not True:
            return
        self.alist = self.designParameters()
        self.outputs = tension_welded_design(self.alist)
        print("output list ", self.outputs)

        self.ui.outputDock.setFixedSize(310, 710)
        self.enable_buttons()

        a = self.outputs[list(self.outputs.keys())[0]]
        self.resultObj = self.outputs
        alist = list(self.resultObj.values())

        self.display_output(self.outputs)
        self.display_log_to_textedit()
        isempty = [True if val != '' else False for ele in alist for val in list(ele.values())]

        if isempty[0] == True:
            status = self.resultObj['Tension_Force']['Design_Status']
            self.call_3DModel("gradient_bg")
            if status is True:
                self.call_2D_drawing("All")
            else:
                # self.ui.btn_pitchDetail.setDisabled(False)
                # self.ui.btn_plateDetail.setDisabled(False)
                # self.ui.btn_plateDetail_2.setDisabled(False)
                # self.ui.btn_stiffnrDetail.setDisabled(False)
                self.ui.chkBx_connector.setDisabled(True)
                self.ui.chkBx_columnSec.setDisabled(True)
                self.ui.chkBx_beamSec.setDisabled(True)
                self.ui.btn3D.setDisabled(True)

    def display_output(self, outputObj):
        for k in list(outputObj.keys()):
            for value in list(outputObj.values()):
                if list(outputObj.items()) == " ":
                    resultObj = outputObj
                else:
                    resultObj = outputObj
        print(resultObj)

        tension_yielding = resultObj['Tension_Force']['Yielding']
        self.ui.txt_tension_yielding.setText(str(tension_yielding))

        tension_rupture = resultObj['Tension_Force']['Rupture']
        self.ui.txt_tension_rupture.setText(str(tension_rupture))

        tension_block_shear = resultObj['Tension_Force']['Block_Shear']
        self.ui.txt_tension_block_shear.setText(str(tension_block_shear))

        tension_efficiency = resultObj['Tension_Force']['Efficiency']
        self.ui.txt_efficiency.setText(str(tension_efficiency))

        tension_slenderness = resultObj['Tension_Force']['Slenderness']
        self.ui.txt_slender.setText(str(tension_slenderness))

    def display_log_to_textedit(self):
        file = QFile(os.path.join('Tension', 'extnd.log'))
        if not file.open(QtCore.QIODevice.ReadOnly):
            QMessageBox.information(None, 'info', file.errorString())
        stream = QtCore.QTextStream(file)
        self.ui.textEdit.clear()
        self.ui.textEdit.setHtml(stream.readAll())
        vscroll_bar = self.ui.textEdit.verticalScrollBar()
        vscroll_bar.setValue(vscroll_bar.maximum())
        file.close()

    def disable_buttons(self):
        self.ui.btn_CreateDesign.setEnabled(False)
        self.ui.btn_SaveMessages.setEnabled(False)
        self.ui.btnFront.setEnabled(False)
        self.ui.btnTop.setEnabled(False)
        self.ui.btnSide.setEnabled(False)
        self.ui.btn3D.setEnabled(False)
        self.ui.chkBx_columnSec.setEnabled(False)
        self.ui.chkBx_beamSec.setEnabled(False)
        self.ui.chkBx_connector.setEnabled(False)
        self.ui.action_save_input.setEnabled(False)
        self.ui.actionCreate_design_report.setEnabled(False)
        self.ui.actionSave_3D_model.setEnabled(False)
        self.ui.actionSave_log_messages.setEnabled(False)
        self.ui.actionSave_current_image.setEnabled(False)
        self.ui.actionSave_Front_View.setEnabled(False)
        self.ui.actionSave_Side_View.setEnabled(False)
        self.ui.actionSave_Top_View.setEnabled(False)
        self.ui.menuGraphics.setEnabled(True)

    def enable_buttons(self):
        self.ui.btn_CreateDesign.setEnabled(True)
        self.ui.btn_SaveMessages.setEnabled(True)
        self.ui.btnFront.setEnabled(True)
        self.ui.btnTop.setEnabled(True)
        self.ui.btnSide.setEnabled(True)
        self.ui.btn3D.setEnabled(True)
        self.ui.chkBx_columnSec.setEnabled(True)
        self.ui.chkBx_beamSec.setEnabled(True)
        self.ui.chkBx_connector.setEnabled(True)
        self.ui.action_save_input.setEnabled(True)
        self.ui.actionCreate_design_report.setEnabled(True)
        self.ui.actionSave_3D_model.setEnabled(True)
        self.ui.actionSave_log_messages.setEnabled(True)
        self.ui.actionSave_current_image.setEnabled(True)
        self.ui.actionSave_Front_View.setEnabled(True)
        self.ui.actionSave_Side_View.setEnabled(True)
        self.ui.actionSave_Top_View.setEnabled(True)
        self.ui.menuGraphics.setEnabled(True)

    def reset_btnclicked(self):
        """
		Returns:
		"""
        self.ui.combo_conn_loc.setCurrentIndex(0)
        self.ui.combo_sectiontype.setCurrentIndex(0)
        self.ui.combo_sectionsize.setCurrentIndex(0)
        self.ui.txt_Fu.clear()
        self.ui.txt_Fy.clear()
        self.ui.txt_Member_length.clear()
        self.ui.txt_Tensionforce.clear()
        self.ui.txt_plate_thk.clear()
        self.ui.txt_inline_tension.clear()
        self.ui.txt_oppline_tension.clear()
        self.ui.combo_end1_cond1.setCurrentIndex(0)
        self.ui.combo_end1_cond2.setCurrentIndex(0)
        self.ui.combo_end2_cond1.setCurrentIndex(0)
        self.ui.combo_end2_cond2.setCurrentIndex(0)

        self.ui.btnFront.setDisabled(True)
        self.ui.btnTop.setDisabled(True)
        self.ui.btnSide.setDisabled(True)

        self.display.EraseAll()
        self.designPrefDialog.save_default_para()

    def get_sectiondata(self, text):

        self.ui.combo_sectionsize.clear()
        member_type = text
        membdata = get_membercombolist(member_type)
        old_beamdata = get_oldbeamcombolist()
        combo_section = ''
        self.ui.combo_sectionsize.addItems(membdata)
        combo_section = self.ui.combo_sectionsize
        self.color_oldDatabase_section(old_beamdata, membdata, combo_section)

    def color_oldDatabase_section(self, old_section, intg_section, combo_section):
        """
		Args:
			old_section: Old database
			intg_section: Integrated database
			combo_section: Contents of database
		Returns: Differentiate the database by color code
		"""
        for col in old_section:
            if col in intg_section:
                indx = intg_section.index(str(col))
                combo_section.setItemData(indx, QBrush(QColor("red")), Qt.TextColorRole)

        duplicate = [i for i, x in enumerate(intg_section) if intg_section.count(x) > 1]
        for i in duplicate:
            combo_section.setItemData(i, QBrush(QColor("red")), Qt.TextColorRole)

    def fetchMembPara(self):
        membertype_sec = self.ui.combo_sectiontype.currentText()
        memberdata_sec = self.ui.combo_sectionsize.currentText()
        dictmembdata = get_memberdata(memberdata_sec, membertype_sec)
        return dictmembdata

    def check_range(self, widget, min_val, max_val):
        """
		Args:
			widget: Fu , Fy lineedit
			min_val: min value
			max_val: max value
		Returns: Check for the value mentioned for the given range
		"""
        text_str = widget.text()
        text_str = int(text_str)
        if (text_str < min_val or text_str > max_val or text_str == ''):
            QMessageBox.about(self, "Error", "Please enter a value between %s-%s" % (min_val, max_val))
            widget.clear()
            widget.setFocus()

    # TODO #
    def check_weld_range(self, widget, lblwidget, uiObj):
        """
		Args:
			widget: Fu , Fy lineedit
			min_val: min value
			max_val: max value
		Returns: Check for the value mentioned for the given range
		"""

        def clear_widget():
            ''' Clear the widget and change the label colour in to red '''
            widget.clear()
            widget.setFocus()
            palette = QPalette()
            palette.setColor(QPalette.Foreground, Qt.red)
            lblwidget.setPalette(palette)
            pass

        dictmemberdata = self.fetchMembPara()

        plate_thick = float(self.ui.txt_plate_thk.text())
        if self.ui.combo_sectiontype.currentText() != "Angles":
            member_d = float(dictmemberdata["D"])
            member_B = float(dictmemberdata["B"])
        else:
            member_leg = dictmemberdata["AXB"]
            leg = member_leg.split("x")
            leg1 = float(leg[0])
            leg2 = float(leg[1])
            min_leg = min(leg1, leg2)
            max_leg = max(leg1, leg2)
        loc = self.ui.combo_conn_loc.currentText()
        if loc == "Flange":
            min_weld_length = round((member_B, 3))
            max_weld_length = round((2 * member_B - 4 * plate_thick), 3)
        elif loc == "Web":
            min_weld_length = round((0.6 * member_d), 3)
            max_weld_length = round((member_d - 2 * plate_thick), 3)
        elif loc == "Back to Back Web":
            min_weld_length = round((2 * 0.6 * member_d), 3)
            max_weld_length = round((2 * member_d), 3)
        elif loc == "Leg":
            min_weld_length = round(min_leg, 3)
            max_weld_length = round(max_leg, 3)
        elif loc == "Star Angles" or loc == "Back to Back Angles":
            min_weld_length = round((min_leg + min_leg), 3)
            max_weld_length = round((max_leg + max_leg), 3)

        text_str = widget.text()

        if text_str == "":
            QMessageBox.about(self, "Error", "Please enter some value")
        else:
            text_str = float(text_str)
            if (text_str < min_weld_length or text_str > max_weld_length or text_str == ''):
                QMessageBox.about(self, "Error",
                                  "Please enter a value between {}-{}".format(min_weld_length, max_weld_length))
                widget.clear()
                widget.setFocus()
            else:
                pass

    # TODO #

    def validate_fu_fy(self, fu_widget, fy_widget, current_widget, lblwidget):
        '''(QlineEdit,QLable,Number,Number)---> NoneType
		Validating F_u(ultimate Strength) greater than F_y (Yeild Strength) textfields
		'''
        try:
            fu_value = float(fu_widget.text())
        except ValueError:
            fu_value = 0.0

        try:
            fy_value = float(fy_widget.text())
        except ValueError:
            fy_value = 0.0

        if fy_value > fu_value:
            QMessageBox.about(self, 'Error', 'Yield strength (fy) cannot be greater than ultimate strength (fu)')
            current_widget.clear()
            current_widget.setFocus()
            palette = QPalette()
            palette.setColor(QPalette.Foreground, Qt.red)
            lblwidget.setPalette(palette)
        else:
            palette = QPalette()
            lblwidget.setPalette(palette)

    def call_2D_drawing(self, view):
        """
		Args:
			view: Front, Side & Top view of 2D svg drawings
		Returns: SVG image created through svgwrite package which takes design INPUT and OUTPUT
				 parameters from Extended endplate GUI
		"""
        self.alist = self.designParameters()
        self.result_obj = tension_welded_design(self.alist)
        self.member_data = self.fetchMembPara()
        tension_drawing = Tension_drawing(self.alist, self.result_obj, self.member_data,
                                          self.folder)

        status = self.resultObj['Tension_Force']['Design_Status']
        if status is True:
            if view != "All":
                if view == "Front":
                    filename = os.path.join(self.folder, "images_html", "Front.svg")

                elif view == "Side":
                    filename = os.path.join(self.folder, "images_html", "Side.svg")

                else:
                    filename = os.path.join(self.folder, "images_html", "Top.svg")

                tension_drawing.save_to_svg(filename, view)
                svg_file = SvgWindow()
                svg_file.call_svgwindow(filename, view, self.folder)
            else:
                fname = ''
                tension_drawing.save_to_svg(fname, view)
        else:
            QMessageBox.about(self, 'Information', 'Design Unsafe: %s view cannot be viewed' % (view))

    def dockbtn_clicked(self, widgets):
        """
		Args:
			widgets: Input , Output dock
		Returns: Dock & undock the widgets
		"""
        flag = widgets.isHidden()
        if flag:
            widgets.show()
        else:
            widgets.hide()

    def show_font_dialogue(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.ui.textEdit.setFont(font)

    def design_report(self):
        design_report_dialog = DesignReportDialog(self)
        design_report_dialog.show()

        fileName = ("Connections\Moment\BCEndPlate\Html_Report.html")
        fileName = str(fileName)
        self.alist = self.designParameters()
        self.result = tension_welded_design(self.alist)
        print("result_obj", self.result)
        self.memb_data = self.fetchBeamPara()
        save_html(self.result, self.alist, self.beam_data, fileName)

    # ===========================  CAD ===========================
    def show_color_dialog(self):

        col = QColorDialog.getColor()
        colorTup = col.getRgb()
        r = colorTup[0]
        g = colorTup[1]
        b = colorTup[2]
        self.display.set_bg_gradient_color(r, g, b, 255, 255, 255)

    def create_2D_CAD(self):
        '''
		Returns: The 3D model of extendedplate depending upon component selected
		'''
        pass

    # self.ExtObj = self.create_cad()
    # if self.component == "Column":
    # 	final_model = self.ExtObj.get_column_models()
    #
    # elif self.component == "Beam":
    # 	final_model = self.ExtObj.get_beam_models()
    #
    # elif self.component == "Connector":
    # 	cadlist = self.ExtObj.get_connector_models()
    # 	final_model = cadlist[0]
    # 	for model in cadlist[1:]:
    # 		final_model = BRepAlgoAPI_Fuse(model, final_model).Shape()
    # else:
    # 	cadlist = self.ExtObj.get_models()
    # 	final_model = cadlist[0]
    # 	for model in cadlist[1:]:
    # 		final_model = BRepAlgoAPI_Fuse(model, final_model).Shape()

    # 	return final_model

    def save_3D_cad_images(self):
        pass

    # 	'''
    # 	Returns: Save 3D CAD images in *igs, *step, *stl, *brep format
    # 	'''
    # 	status = self.resultObj['Tension_Force']['Design_Status']
    # 	if status is True:
    # 		if self.fuse_model is None:
    # 			self.fuse_model = self.create_2D_CAD()
    # 		shape = self.fuse_model
    #
    # 		files_types = "IGS (*.igs);;STEP (*.stp);;STL (*.stl);;BREP(*.brep)"
    #
    # 		fileName, _ = QFileDialog.getSaveFileName(self, 'Export', os.path.join(str(self.folder), "untitled.igs"),
    # 												  files_types)
    # 		fName = str(fileName)
    #
    # 		flag = True
    # 		if fName == '':
    # 			flag = False
    # 			return flag
    # 		else:
    # 			file_extension = fName.split(".")[-1]
    #
    # 			if file_extension == 'igs':
    # 				IGESControl.IGESControl_Controller().Init()
    # 				iges_writer = IGESControl.IGESControl_Writer()
    # 				iges_writer.AddShape(shape)
    # 				iges_writer.Write(fName)
    #
    # 			elif file_extension == 'brep':
    #
    # 				BRepTools.breptools.Write(shape, fName)
    #
    # 			elif file_extension == 'stp':
    # 				# initialize the STEP exporter
    # 				step_writer = STEPControl_Writer()
    # 				Interface_Static_SetCVal("write.step.schema", "AP203")
    #
    # 				# transfer shapes and write file
    # 				step_writer.Transfer(shape, STEPControl_AsIs)
    # 				status = step_writer.Write(fName)
    #
    # 				assert (status == IFSelect_RetDone)
    #
    # 			else:
    # 				stl_writer = StlAPI_Writer()
    # 				stl_writer.SetASCIIMode(True)
    # 				stl_writer.Write(shape, fName)
    #
    # 			self.fuse_model = None
    #
    # 			QMessageBox.about(self, 'Information', "File saved")
    # 	else:
    # 		self.ui.actionSave_3D_model.setEnabled(False)
    # 		QMessageBox.about(self, 'Information', 'Design Unsafe: 3D Model cannot be saved')
    #
    def save_CAD_images(self):
        pass

    # status = self.resultObj['Tension_Force']['Design_Status']
    # 	if status is True:
    #
    # 		files_types = "PNG (*.png);;JPEG (*.jpeg);;TIFF (*.tiff);;BMP(*.bmp)"
    # 		fileName, _ = QFileD ialog.getSaveFileName(self, 'Export', os.path.join(str(self.folder), "untitled.png"),
    # 												  files_types)
    # 		fName = str(fileName)
    # 		file_extension = fName.split(".")[-1]
    #
    # 		if file_extension == 'png' or file_extension == 'jpeg' or file_extension == 'bmp' or file_extension == 'tiff':
    # 			self.display.ExportToImage(fName)
    # 			QMessageBox.about(self, 'Information', "File saved")
    # 	else:
    # 		self.ui.actionSave_current_image.setEnabled(False)
    # 		QMessageBox.about(self, 'Information', 'Design Unsafe: CAD image cannot be saved')
    #
    def call_zoomin(self):
        self.display.ZoomFactor(2)

    def call_zoomout(self):
        self.display.ZoomFactor(0.5)

    def call_rotation(self):
        self.display.Rotation(15, 0)

    def call_pannig(self):
        self.display.Pan(50, 0)

    def clear_log_messages(self):
        self.ui.textEdit.clear()

    # TODO : Anand, add member data and diplay
    def create_cad(self):

        self.member_data = self.fetchMembPara()
        self.alist = self.designParameters()

        if self.alist["Member"]["SectionType"] == "Angles":
            # member_leg = 50 x 50		#memb_data["AXB"]
            # leg = self.member_leg.split("x")
            leg1 = 50  # self.leg[0]
            leg2 = 50  # self.leg[1]
            # leg_min = min(float(self.leg1),float(self.leg2))
            # leg_max = max(float(self.leg1),float(self.leg2))
            t = 5  # float(memb_data["t"])
            member_length = 100  # 750.0
            weld_ht = t
            plate_ht = 2 * leg1

            member = Angle(L=member_length, A=leg1, B=leg2, T=t, R1=0, R2=0)

        else:
            member_tw = float(self.member_data["tw"])  # 1.5	 #float(memb_data["tw"])
            member_T = float(self.member_data["T"])  # 2	#float(memb_data["T"])
            member_d = float(self.member_data["D"])  # 40	#float(memb_data["D"])
            member_B = float(self.member_data["B"])  # 20	#float(memb_data["B"])
            member_length = 750  # 750.0
            weld_ht = member_tw
            plate_ht = 2 * member_d

            member = Channel(B=member_B, T=member_T, D=member_d, t=member_tw, R1=0, R2=0, L=member_length)

        plate = Plate(W=float(self.alist["Weld"]["inline_tension"]), L=plate_ht, T=float(
            self.alist["Weld"]["Platethickness"]))  # (W=outputobj["Plate"]["Width"], L=outputobj["Plate"]["Height"],
        # T=  float(self.alist["Weld"]["Platethickness"]))

        inline_weld = FilletWeld(b=weld_ht, h=weld_ht, L=float(self.alist["Weld"]["inline_tension"]) / 2)
        opline_weld = FilletWeld(b=weld_ht, h=weld_ht, L=float(self.alist["Weld"]["oppline_tension"]))

        # (b=float(self.alist["Weld"]["Web (mm)"]), h=float(self.alist["Weld"]["Web (mm)"]),
        # 					 L=outputobj['Stiffener']['Height'] - outputobj['Stiffener']['NotchBottom'])

        # TODO: edit this input  dictionary for different types late

        # if input_dict["Member"]["SectionType"] == "Beams" or input_dict["Member"]["SectionType"] == "Columns":
        # 	member = ISection(B=member_B, T=member_T, D=member_d, t=member_tw, length=member_length)

        # if input_dict["Member"]["SectionType"] == "Angles":
        # 	member = Angle(L = member_length, A = leg1, B = leg2, T = t)
        #
        # else: #Channels
        #
        # 	member = Channel(B=member_B, T=member_T, D=member_d, t=member_tw, length=member_length)

        # TODO :  Add different sections later

        # 	if alist['Member']['Connectivity'] == "Column web-Beam web":
        # 		conn_type = 'col_web_connectivity'
        # 	else:  # "Column flange-Beam web"
        # 		conn_type = 'col_flange_connectivity'
        #
        # 	# endplate_type = alist['Member']['EndPlate_type']
        # 	if alist['Member']['EndPlate_type'] == "Extended one way":
        # 		endplate_type = "one_way"
        # 	elif alist['Member']['EndPlate_type'] == "Flush end plate":
        # 		endplate_type = "flush"
        # 	else:  # uiObj['Member']['EndPlate_type'] == "Extended both ways":
        # 		endplate_type = "both_way"
        #

        # TODO: Cad file

        tensionCAD = CAD(member, plate, inline_weld, opline_weld, self.alist, self.member_data)

        tensionCAD.create_3DModel()
        return tensionCAD

    def call_3DModel(self, bgcolor):
        # Call to calculate/create the Extended Both Way CAD model
        status = self.resultObj['Tension_Force']['Design_Status']
        if status is True:
            self.create_cad()
            self.ui.btn3D.setChecked(Qt.Checked)
            if self.ui.btn3D.isChecked():
                self.ui.chkBx_columnSec.setChecked(Qt.Unchecked)
                self.ui.chkBx_beamSec.setChecked(Qt.Unchecked)
                self.ui.chkBx_connector.setChecked(Qt.Unchecked)
                self.ui.mytabWidget.setCurrentIndex(0)

            # Call to display the Extended Both Way CAD model
            self.display_3DModel("Model", bgcolor)
        else:
            self.display.EraseAll()

    def display_3DModel(self, component, bgcolor):
        self.component = component

        self.display.EraseAll()
        self.display.View_Iso()
        # self.display.StartRotation(2000,0)
        self.display.FitAll()
        # self.display.Rotation(2000, 0)

        # self.display.DisableAntiAliasing()
        # if bgcolor == "gradient_bg":
        #
        # 	self.display.set_bg_gradient_color(51, 51, 102, 150, 150, 170)
        # else:
        # 	self.display.set_bg_gradient_color(255, 255, 255, 255, 255, 255)

        # 	# ExtObj is an object which gets all the calculated values of CAD models
        self.ExtObj = self.create_cad()

        self.display.View_Iso()
        osdag_display_shape(self.display, self.ExtObj.get_models(), update=True)

    # # =================================================================================
    def open_about_osdag(self):
        dialog = MyAboutOsdag(self)
        dialog.show()

    def open_tutorials(self):
        dialog = MyTutorials(self)
        dialog.show()

    def open_ask_question(self):
        dialog = MyAskQuestion(self)
        dialog.show()

    def design_examples(self):
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ResourceFiles', 'design_example',
                                 '_build', 'html')
        for html_file in os.listdir(root_path):
            if html_file.startswith('index'):
                if sys.platform == ("win32" or "win64"):
                    os.startfile("%s/%s" % (root_path, html_file))
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, "%s/%s" % (root_path, html_file)])


def set_osdaglogger():
    global logger
    if logger is None:

        logger = logging.getLogger("osdag")
    else:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)

    # create the logging file handler
    fh = logging.FileHandler(os.path.join('Tension', 'extnd.log'), mode='a')

    # ,datefmt='%a, %d %b %Y %H:%M:%S'
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    formatter = logging.Formatter('''
	<div  class="LOG %(levelname)s">
		<span class="DATE">%(asctime)s</span>
		<span class="LEVEL">%(levelname)s</span>
		<span class="MSG">%(message)s</span>
	</div>''')
    formatter.datefmt = '%a, %d %b %Y %H:%M:%S'
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def launch_tension_welded_controller(osdagMainWindow, folder):
    set_osdaglogger()
    # --------------- To display log messages in different colors ---------------
    rawLogger = logging.getLogger("raw")
    rawLogger.setLevel(logging.INFO)
    # file_handler = logging.FileHandler(os.path.join('Connections','Moment','BCEndPlate','extnd.log'), mode='w')
    file_handler = logging.FileHandler("Tension/extnd.log", mode='w')
    formatter = logging.Formatter('''%(message)s''')
    file_handler.setFormatter(formatter)
    rawLogger.addHandler(file_handler)

    # Linux
    # '''<link rel="stylesheet" type="text/css" href=''' + os.path.join('Connections', 'Moment', 'BCEndPlate',
    # 																	  'log.css') + '''/>''')

    # Windows
    rawLogger.info('''<link rel="stylesheet" type="text/css" href="Tension/log.css"/>''')

    # ----------------------------------------------------------------------------
    module_setup()
    window = Maincontroller(folder)
    osdagMainWindow.hide()
    window.show()
    window.closed.connect(osdagMainWindow.show)


if __name__ == "__main__":

    set_osdaglogger()
    # --------------- To display log messages in different colors ---------------
    rawLogger = logging.getLogger("raw")
    rawLogger.setLevel(logging.INFO)
    # fh = logging.FileHandler(os.path.join('Connections','Moment','BCEndPlate','extnd.log'), mode="w")
    fh = logging.FileHandler(os.path.join('..', 'extnd.log'), mode='w')

    formatter = logging.Formatter('''%(message)s''')
    fh.setFormatter(formatter)
    rawLogger.addHandler(fh)
    # rawLogger.info('''<link rel="stylesheet" type="text/css" href="Connections\Moment\BCEndPlate\log.css"/>''')	#Linux
    rawLogger.info(
        '''<link rel="stylesheet" type="text/css" href="Tension/log.css"/>''')  # Windows
    # ----------------------------------------------------------------------------
    # folder_path = "D:\Osdag_Workspace\extendedendplate"
    app = QApplication(sys.argv)
    module_setup()
    folder_path = "/home/ajmalbabums/Osdag_workspace"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path, 0o755)
    image_folder_path = os.path.join(folder_path, 'images_html')
    if not os.path.exists(image_folder_path):
        os.mkdir(image_folder_path, 0o755)

    window = Maincontroller(folder_path)
    window.show()
    sys.exit(app.exec_())
