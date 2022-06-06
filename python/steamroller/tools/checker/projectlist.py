
def projectFilters( project = 'Default', step = 'Model', assetName = 'assetName' ):
      
  """
  In this function checker are assigned for each project, 
  assigning the "step" as a key an as a value : ( checkers name , priority level , args )

  Modeling checker:
  'constructionHistory' , 'resetTransformsOrigin' , 'freezeTransform' , 'symmetry' , 'allQuads' ,
  'nGons' , 'nonManifoldGeometry' , 'laminaFaces' , 'emptyGroups' , 'noIdenticalNames' , 'noIdenticalShapeNames' ,
  'hierarchy' , 'orientation' , 'onAboveOrigin' , 'deleteCustomCameras' , 'noKeyframes', 'noLayers' , 'noCurves' , 
  'extensionFile' , 'unknowNodes' 

  LookDev checker:
  'clearDeformers', 'blendShape', 'delNonDeformHistory', 'flagGeoWithTransform', 'flagObjWithDeformHistory',
  'uvSetName', 'multipleUVSet', 'materialPrefix', 'defaultMaterialType', 'deleteUnusedNode', 'noKeyframes',
  'faceWithoutMaterial'


  :checker: key name for the check method.
  :priority:  1 = critical must have to be correct, 2 = warning.
  :args: additional arguments needed by the checker. 

  :param project: project name.
  :param step: step name (model , surfacing, layout)
  :param assetName: asset name form the assigned task. 

  :return: [ checkers (str), priority (int), args ]
  """
  # Mesh name convention. 
  default_meshName_convention = {'prefix': 'GEO_', 'sufix':'', 'allowedPrefix': '', 'allowedSufix': '', 'tgtPrefix': 'TGT_' }


  projectFilter = { 'default' : 
                    { 'model' : 
                      [ 
                      ( 'constructionHistory'   , 1 , [ 'groupId', 'shadingEngine' ] ),
                      ( 'resetTransformsOrigin' , 2 ),
                      ( 'freezeTransform'       , 2 ),
                      ( 'symmetry'              , 2 , 'x' ), # X axis symmetry ( world space )
                      ( 'allQuads'              , 2 ),
                      ( 'nGons'                 , 1 ), 
                      ( 'nonManifoldGeometry'   , 1 ),
                      ( 'laminaFaces'           , 1 ),
                      ( 'emptyGroups'           , 1 ),
                      ( 'hierarchy'             , 1  , assetName ),      # need current asset name. 
                      ( 'noIdenticalNames'      , 1 ),
                      ( 'groupName'             , 1  , ( assetName, '', '_GRP' ) ), # ( assetName, prefix, sufix )
                      ( 'meshName'              , 1  , assetName,   default_meshName_convention ), # ( assetName, dict,  )
                      ( 'noIdenticalShapeNames' , 1 ),
                      ( 'orientation'           , 1  , (1, 1, 1) ),      # XYZ 1,1,1 = Yup Z front. 
                      ( 'onAboveOrigin'         , 1 ),
                      ( 'deleteCustomeCameras'  , 1 ),
                      ( 'noKeyframes'           , 1 ),
                      ( 'noLayers'              , 1 ),
                      ( 'noCurves'              , 1 ),
                      ( 'extensionFile'         , 1  , 'ma' ), 
                      ( 'unknowNodes'           , 1 ),
                      ],
                    
                    'lookDev':
                    [
                    ( 'clearDeformers'          , 1 , [ 'blendShape' ] ), # Deformers to clean
                    ( 'delNonDeformHistory'     , 1 ),
                    ( 'flagGeoWithTransform'    , 2 ),
                    ( 'flagObjWithDeformHistory', 2 ),
                    ( 'uvSetName'               , 1 ),
                    ( 'multipleUVSet'           , 2 ),
                    ( 'materialPrefix'          , 1 , 'Mat_'), # Material prefix
                    ( 'defaultMaterialType'     , 1 , 'lambert' ), # Set default material type
                    ( 'deleteUnusedNode'        , 2 ),
                    ( 'noKeyframes'             , 1 ),
                    ( 'faceWithoutMaterial'     , 1 ),
                    ],

                    'layout':
                    [
                    ( 'assemblyHierarchyLayout' , 1 , ['Character', 'Enviroment', 'Prop', 'Camera', 'Temp', 'Crowd'] ),
                    ( 'layoutHierarchy'         , 1 , ['Character', 'Enviroment', 'Prop', 'Camera', 'Temp', 'Crowd'] ),
                    ( 'cameraHierarchy'         , 1 , 'Camera', ['Character', 'Enviroment', 'Prop', 'Temp', 'Crowd'] ), # Parent group, exceptions.               
                    ( 'sceneConstrain'          , 1 , ['Camera', 'Temp'] ), # Allowed objects groups with constrains 
                    ( 'timelineOffset'          , 1, 1001 ), # timeoffset
                    ( 'singleAudioTrack'        , 1 ),
                    ( 'checkAudioOffset'        , 1, 1001 ), 
                    ( 'cameraName'              , 1, 'shotcam_'), # prefix 
                    ( 'shotnodeName'            , 1, 'shotnode_'), # prefix
                    ( 'shotCameraCongruence'    , 1, 'prefix'), # condition key prefix or sufix.
                    ( 'shotNodeScale'           , 1 ),
                    ( 'extensionFile'           , 1  , 'ma' ), 
                    ( 'emptyGroupsLayout'       , 1 , ['Character', 'Enviroment', 'Prop', 'Camera', 'Temp', 'Crowd'] ),
                    ( 'deleteUnusedNode'        , 2 ),
                    ( 'noLayers'                , 1 ),
                    ( 'cleanLights'             , 2 , True ), # Priority , omit Namespace bool 
                    ( 'checkNamespace'          , 1 )

                    ],

                    'animation':
                    [
                    ( 'cleanLights'             , 1 , True ), # Priority , omit Namespace bool 
                    ( 'noLayers'                , 1 ),
                    ( 'animLayer'               , 2 ),
                    ( 'defaultRotationOrder'    , 2 , ( 'tag', '_prefix', '_ctrl', 'attr' ) ), # ( filter type, prefix, sufix, attrData )
                    ( 'auidoTrackAnim'          , 2 ),
                    ( 'deleteCustomeCameras'    , 1 ),
                    ( 'junkNodesAnim'           , 2 ),
                    ]

                    },
                  }

  return projectFilter[project][step]

