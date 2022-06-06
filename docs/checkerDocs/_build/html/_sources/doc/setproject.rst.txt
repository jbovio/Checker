.. _setNewProject:

Set new project
=======================

Setps
---------

1. open ../lib/projectlist.py
2. Inside projectlist.py there is a function called “projectFilters” in order to
set a new project required add a new key in projectFilter dictionary and indicate 
the check functions per step and project. 
3. e.g. {projectName: { step: check function }, { step2: check funtion }}
4. Some funtions required specific parameters can be set in the key value. 


.. code-block::
    
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
                    ( 'cleanConstraints'        , 1 ),
                    ],

                    'animation':
                    [
                    ( 'cleanLights'             , 1 , True ), # Priority , omit Namespace bool 
                    ( 'noLayers'                , 1 ),
                    ( 'animLayer'               , 2 ),
                    ( 'defaultRotationOrder'    , 2 , ( 'tag', '_prefix', '_ctrl', 'attr' ) ), # ( filter type, prefix, sufix, attrData )
                    ( 'auido'                   , 2 ),
                    ( 'deleteCustomeCameras'    , 1 ),
                    ( 'junkNodesAnim'           , 2 ),
                    ]

                    },
                  }
