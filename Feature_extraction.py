import os
import json
# from __future__ import print_function
import logging
import SimpleITK as sitk
import radiomics
from radiomics import featureextractor
import xlsxwriter
import xlrd
import operator
import scipy
import trimesh
import numpy
Eex0lis = []
Ecnt = 0


 with open("data.json",'r') as load_f:
    pathlist = json.load(load_f)
    print(pathlist)
imageName = ''
maskName = ''
cnt = 0
for pathdicom in pathlist:
  PathDicom = pathdicom
  listpic = os.listdir(pathdicom)
  cnt += 1

for listnum in listpic:
    if 'data' in listnum and 'nrrd' in listnum: # and 'patient' not in listnum:
      path_nii_nrrd = os.path.join(pathdicom, listnum)
      maskName = path_nii_nrrd  
      break
  for listnum in listpic:
    if 'dcm5' in listnum and 'nrrd' in listnum:
      path_dcm_nrrd = os.path.join(pathdicom, listnum)
      imageName = path_dcm_nrrd  # dcm.nrrd 
      break
  print("Processing section", cnt, 'sample')
  print(imageName, maskName)
  mask = sitk.ReadImage(maskName)
  image = sitk.ReadImage(imageName)

  print(image.GetSize(), mask.GetSize())

  path_fea_all = r'H:\T790M_Result\Features\EGFR-_old_T1_T.xlsx'  

  print('The folder being processed now is：', PathDicom)
  print('Start feature extraction')
  radiomics.setVerbosity(logging.INFO)
  logger = radiomics.logger
  logger.setLevel(logging.DEBUG) 
  handler = logging.FileHandler(filename='testLog.txt', mode='w')
  formatter = logging.Formatter("%(levelname)s:%(name)s: %(message)s")
  handler.setFormatter(formatter)
  logger.addHandler(handler)
 params = r'E:\Jupyter\pyradiomics-master\examples\exampleSettings\Params.yaml'
  settings = {}

  settings['label'] =3
  settings['binWidth'] = 25
# settings['resampledPixelSpacing'] = None  # [3,3,3] is an example for defining resampling (voxels with size 3x3x3mm)  # settings['resampledPixelSpacing'] = [0.1,0.1,1]  # This is an example for defining resampling (voxels with size 3x3x3mm)
  settings['interpolator'] = sitk.sitkBSpline
  settings['normalize'] = True
  settings['normalizeScale'] = 100
  settings['geometryTolerance'] = 10000000
  settings['minimumROIDimensions'] = 1
  settings['minimumROISize'] = None
  settings['correctMask'] = True

  extractor = featureextractor.RadiomicsFeatureExtractor(**settings)

  extractor.enableAllFeatures()
  extractor.enableAllImageTypes()
  extractor.enableImageTypeByName('LoG', customArgs={'sigma': [1.0, 3.0, 5.0]})
  print("Calculating features")
  print('Enabled input images:')
  try:
      featureVector = extractor.execute(imageName, maskName)
      featureVector_sorted = sorted(featureVector.items(), key=operator.itemgetter(0), reverse=False)
      print("Feature calculation completed")
      print("Start writing excell")
      myWorkbook = xlrd.open_workbook(path_fea_all)  
      mySheet_read = myWorkbook.sheet_by_index(0)  
      sheet_row = mySheet_read.nrows  
      sheet_column = mySheet_read.ncols  
      workbook = xlsxwriter.Workbook(path_fea_all)
      worksheet = workbook.add_worksheet()
      print(path_fea_all)
      print(sheet_row)

      if sheet_row > 0:  
        for nrow in range(sheet_row):
          for ncol in range(sheet_column):
            cell_value = mySheet_read.cell_value(nrow, ncol)
            worksheet.write(nrow, ncol, cell_value)  

      if sheet_row == 0:
        sheet_row = sheet_row + 1 
        worksheet.write(sheet_row, 0, imageName)
      else:
        worksheet.write(sheet_row, 0, imageName)

      sheet_column = 1  
      for feature_name in featureVector_sorted:
        worksheet.write(0, sheet_column, feature_name[0])
        worksheet.write(sheet_row, sheet_column, str(feature_name[1]))
        sheet_column = sheet_column + 1

      workbook.close()  
      print("Placed in table")
  except MemoryError:

      Ecnt+=1
      print('Processing section', Ecnt, 'Error files')
      Eex0lis.append(PathDicom)
      pass
  continue

with open("Eex0lis(Error).json", 'w') as f:
    json.dump(Eex0lis, f)
    print("successful write")
