
import imp

from steamroller.tools.checker import model
imp.reload( model )
modelingCheck = model.Model()

from steamroller.tools.checker import lookdev
imp.reload( lookdev )
lookdevCheck = lookdev.Lookdev()

from steamroller.tools.checker import anim
imp.reload( anim )
animationCheck = anim.Animation()

from steamroller.tools.checker import layout
imp.reload( layout )
layoutCheck = layout.Layout()


import maya.cmds as mc
import pymel.core as pm


class Checker():

    def checkList(self, check = '', args = None ):
        """
        Contains a checker dictonary by department.

        sufix "_check": Refers to the method who return the results(Dic)
            results = {'state': None, 'note': note, 'fixBtn': None, 'extraBtn': None }

        sufix "_fix": Refers to the method that corrects the error.

        sufix "_extra": Refers to the exclusive method for the checker.

            :state:  (int)  1 True , 2 False, 3 Warning.
            :note:   (str) Description, commnet, general information to display in UI column. 
            :fixBtn: (bool) Method to correct the error. 
            :extraBtn: ( [ bool, str ] ) [ Add an extra function if the method returns false, button lable ] 

            # Checker example.
            'keyName' : 'keyName_check',  # Actual checker
            'keyName_fix' : 'keyName_fix', # Solution 
            'keyName_extra' : 'keyName_select', # Select checked nodes 

        :param check: (str) key name to idicate the method. 
        :param args: project-specific arguments 

        :return: method( args )
        """

        checkerList = {
                        # constructionHistory
                        'constructionHistory': 'deleteHistory_check',
                        'constructionHistory_fix': 'deleteHistory_fix',
                        'constructionHistory_extra': 'deleteHistory_select', 
                        # freezeTransform
                        'freezeTransform': 'freezeTransform_check',
                        'freezeTransform_fix': 'freezeTransform_fix',
                        'freezeTransform_extra': 'freezeTransform_select',
                        # resetTransformsOrigin
                        'resetTransformsOrigin': 'resetTransformsOrigin_check',
                        'resetTransformsOrigin_fix': 'resetTransformsOrigin_fix',
                        'resetTransformsOrigin_extra': 'resetTransformsOrigin_select',
                        # Symmetry
                        'symmetry': 'symmetry_check',
                        'symmetry_extra': 'symmetry_select',
                        # Quads
                        'allQuads': 'allQuads_check',
                        'allQuads_extra': 'allQuads_select',
                        # N-Gons
                        'nGons': 'nGons_check',
                        'nGons_fix': 'nGons_fix',
                        'nGons_extra': 'nGons_select',
                        # Non-Manifold Geometry
                        'nonManifoldGeometry': 'nonManifoldGeo_check',
                        'nonManifoldGeometry_extra': 'nonManifoldGeo_select',
                        # Lamina Faces.
                        'laminaFaces': 'laminaFace_check',
                        'laminaFaces_extra': 'laminaFace_select',
                        # Empty groups.
                        'emptyGroups': 'emptyGroups_check',
                        'emptyGroups_fix': 'emptyGroups_fix',
                        'emptyGroups_extra': 'emptyGroups_select',
                        # No identical names
                        'noIdenticalNames': 'noIdenticalNames_check',
                        'noIdenticalNames_extra': 'noIdenticalNames_select',
                        # No identical shapen names
                        'noIdenticalShapeNames': 'noIdenticalShapeNames_check',
                        'noIdenticalShapeNames_fix': 'noIdenticalShapeNames_fix',
                        'noIdenticalShapeNames_extra': 'noIdenticalShapeNames_select',
                        # Hierarchy
                        'hierarchy': 'hierarchy_check',
                        'hierarchy_fix': 'hierarchy_fix',
                        'hierarchy_extra': 'hierarchy_select',
                        # Orientation 
                        'orientation': 'orientation_check',
                        'orientation_extra': 'orientation_select',
                        # On above origin.
                        'onAboveOrigin': 'onAboveOrigin_check',
                        'onAboveOrigin_extra': 'onAboveOrigin_select',
                        # Delete custom cameras.
                        'deleteCustomeCameras': 'deleteCustomeCameras_check',
                        'deleteCustomeCameras_fix': 'deleteCustomeCameras_fix',
                        'deleteCustomeCameras_extra': 'deleteCustomeCameras_select',
                        # No keyframes.
                        'noKeyframes': 'noKeyframes_check',
                        'noKeyframes_fix': 'noKeyframes_fix',
                        'noKeyframes_extra': 'noKeyframes_select',
                        # No layers.
                        'noLayers': 'noLayers_check',
                        'noLayers_fix': 'noLayers_fix',
                        # No curves.
                        'noCurves': 'noCurves_check',
                        'noCurves_fix': 'noCurves_fix',
                        'noCurves_extra': 'noCurves_select',
                        # Extension file.
                        'extensionFile': 'extensionFile_check',
                        # Unknownodes.
                        'unknowNodes': 'unknowNodes_check',
                        'unknowNodes_fix': 'unknowNodes_fix',
                        'unknowNodes_extra': 'unknowNodes_select',
                        # Group name convention.
                        'groupName': 'groupName_check',
                        'groupName_fix': 'groupName_fix',
                        'groupName_extra': 'groupName_select',
                        # Mesh name convention.
                        'meshName': 'meshName_check',
                        'meshName_fix': 'meshName_fix',
                        'meshName_extra': 'meshName_select',
                       }

        lookdevList =   {
                        # Clear deformers 
                        'clearDeformers': 'clearDeformers_check',
                        'clearDeformers_fix': 'clearDeformers_fix',
                        'clearDeformers_extra': 'clearDeformers_select',
                        # Delte all non-deformer history.
                        'delNonDeformHistory': 'delNonDeformHistory_check',
                        # Flag DAG objects with transforms. 
                        'flagGeoWithTransform': 'flagGeoWithTransform_check',
                        'flagGeoWithTransform_extra': 'flagGeoWithTransform_select',
                        # Flag objects with deform history.
                        'flagObjWithDeformHistory': 'flagObjWithDeformHistory_check',
                        'flagObjWithDeformHistory_extra': 'flagObjWithDeformHistory_select',
                        # UV set name
                        'uvSetName': 'uvSetName_check',
                        'uvSetName_fix': 'uvSetName_fix',
                        'uvSetName_extra': 'uvSetName_select',
                        # Objects with multiple UV set.
                        'multipleUVSet': 'multipleUVSet_check',
                        'multipleUVSet_extra': 'multipleUVSet_select',
                        # Material Prefix
                        'materialPrefix': 'materialPrefix_check',
                        'materialPrefix_fix': 'materialPrefix_fix',
                        'materialPrefix_extra': 'materialPrefix_select',
                        # Default material type.
                        'defaultMaterialType': 'defaultMaterialType_check',
                        'defaultMaterialType_extra': 'defaultMaterialType_select',
                        # Delete unused nodes.
                        'deleteUnusedNode': 'deleteUnusedNode_check',
                        # Faces with initial shading group.
                        'faceWithoutMaterial': 'faceWithoutMaterial_check',
                        'faceWithoutMaterial_extra': 'faceWithoutMaterial_select',
                        }

        animationList = {
                    # Lights. 
                    'cleanLights': 'cleanLights_check',
                    'cleanLights_fix': 'cleanLights_fix',
                    'cleanLights_extra': 'cleanLights_select',
                    # Animation layer.
                    'animLayer': 'animLayer_check',
                    'animLayer_fix': 'animLayer_fix',
                    'animLayer_extra': 'animLayer_select',
                    # Rotation order.
                    'defaultRotationOrder': 'defaultRotationOrder_check',
                    'defaultRotationOrder_fix': 'defaultRotationOrder_fix',
                    'defaultRotationOrder_extra': 'defaultRotationOrder_select',
                    # Junk nodes
                    'junkNodesAnim': 'junkNodesAnim_check',
                    'junkNodesAnim_fix': 'junkNodesAnim_fix',
                    'junkNodesAnim_extra': 'junkNodesAnim_select',
                    # Audio
                    'auidoTrackAnim': 'auidoTrackAnim_check',
                    'auidoTrackAnim_fix': 'auidoTrackAnim_fix',
                    'auidoTrackAnim_extra': 'auidoTrackAnim_select',
                    }

        layoutList = {
                    # time offset. 
                    'timelineOffset': 'timelineOffset_check',
                    'timelineOffset_extra': 'timelineOffset_select',
                    # Camera name.
                    'cameraName': 'cameraName_check',
                    'cameraName_extra': 'cameraName_select',
                    # shotnode name.
                    'shotnodeName': 'shotnodeName_check',
                    'shotnodeName_extra': 'shotnodeName_select',
                    # shotCameraCongruence
                    'shotCameraCongruence': 'shotCameraCongruence_check',
                    'shotCameraCongruence_fix': 'shotCameraCongruence_fix',
                    'shotCameraCongruence_extra': 'shotCameraCongruence_select',
                    # Shot scale.
                    'shotNodeScale': 'shotNodeScale_check',
                    'shotNodeScale_extra': 'shotNodeScale_select',
                    # Single audio track
                    'singleAudioTrack': 'singleAudioTrack_check',
                    'singleAudioTrack_extra': 'singleAudioTrack_select',
                    # Audio offset
                    'checkAudioOffset': 'checkAudioOffset_check',
                    'checkAudioOffset_fix': 'checkAudioOffset_fix',
                    'checkAudioOffset_extra': 'checkAudioOffset_select',
                    # Namespace lower case.
                    'checkNamespace': 'checkNamespace_check',
                    # Hierarchy groups.
                    'assemblyHierarchyLayout': 'assemblyHierarchyLayout_check',
                    'assemblyHierarchyLayout_fix': 'assemblyHierarchyLayout_fix',
                    # cameraHierarchy
                    'cameraHierarchy': 'cameraHierarchy_check',
                    'cameraHierarchy_fix': 'cameraHierarchy_fix',
                    'cameraHierarchy_extra': 'cameraHierarchy_select',
                    # emptyGroupsLayout
                    'emptyGroupsLayout': 'emptyGroupsLayout_check',
                    'emptyGroupsLayout_fix': 'emptyGroupsLayout_fix',
                    'emptyGroupsLayout_extra': 'emptyGroupsLayout_select',
                    # sceneConstraint
                    'sceneConstrain': 'sceneConstrain_check',
                    'sceneConstrain_fix': 'sceneConstrain_fix',
                    'sceneConstrain_extra': 'sceneConstrain_select',
                    # layoutHierarchy
                    'layoutHierarchy': 'layoutHierarchy_check',
                    'layoutHierarchy_extra': 'layoutHierarchy_select',
                    }


        # Modeling check
        if check in checkerList.keys():
            method = eval('modelingCheck.{0}'.format( checkerList[check] ) )

        # LookDev checker
        elif check in lookdevList.keys():
            method = eval('lookdevCheck.{0}'.format( lookdevList[check] ) )

        # Animation checker
        elif check in animationList.keys():
            method = eval('animationCheck.{0}'.format( animationList[check] ) )
        
        # Layout checker
        elif check in layoutList.keys():
            method = eval('layoutCheck.{0}'.format( layoutList[check] ) )

        else:
            method = eval('self.null') # If checker dose not found.

        # Run method.
        return method( args )


    def null(self, *args ):
        """
        When checker is not listed or exist return a null fucntion and warning.
        :return: { state: None,  note: warning, fixBtn: None, extraBtn: None }
        """
        mc.warning ( 'Missing method.' )
        note = 'Missing method, request pipeline assistance.'
        return {'state': None, 'note': note, 'fixBtn': None, 'extraBtn': None }
