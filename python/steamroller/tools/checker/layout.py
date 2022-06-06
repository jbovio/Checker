
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm
import re

class Layout():

    def assemblyHierarchyLayout( self, layoutGrps = [] ):
        """
        Collect all objects that are not under the main asset group.

        :return: list of assemblies dag objects.
        :rtype: string[]
        """

        # List assemblies 
        assemblies = mc.ls( assemblies = True )

        missingGrps = []

        for grp in layoutGrps:
            if not grp in assemblies:
                missingGrps.append( grp )

        return missingGrps

    def assemblyHierarchyLayout_fix( self, *args ):
        
        layoutGrps = args[0][1]

        for grp in layoutGrps:
            if not pm.objExists( grp ):

                g = pm.createNode( 'transform', n = grp )
                g.useOutlinerColor.set( 1 )
                g.outlinerColor.set( 0,1,0 )

    def assemblyHierarchyLayout_check( self, *args ):

        priority = args[0][0]
        layoutGrps = args[0][1]
        missingGrps = self.assemblyHierarchyLayout( layoutGrps )

        if missingGrps:
    
            state = 2 # Error state
            note = 'Error, Missing hierarchy groups : \n ( {0} )'.format( missingGrps )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, Missing hierarchy groups : \n ( {0} )'.format( missingGrps )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ False, '' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def cameraHierarchy( self, parentGroup = 'Camera' ):

        camerasShape = pm.ls( type = 'camera' )

        cameras = []
        for c in camerasShape:
            cParent = c.getParent()

            if cParent.name() in  ['persp', 'front', 'side', 'top']:
                continue
            else:
                cameras.append( cParent )

        # 
        outOfHierarchy = []

        for obj in cameras:
            # convert obj to pyObj
            currentObj = pm.PyNode(obj)

            # look the last parent
            while pm.listRelatives(currentObj.name(), p=True):
                currentObj = pm.listRelatives(currentObj.name(), p=True)[0]

            if not currentObj.name() == parentGroup:
                outOfHierarchy.append( obj )

        return outOfHierarchy

    def cameraHierarchy_select( self, *args ):
        
        parentGroup = args[0][1]
        cams = self.cameraHierarchy( parentGroup )

        pm.select( cams )

    def cameraHierarchy_fix( self, *args ):

        parentGroup = args[0][1]
        exceptions = args[0][2]

        cams = self.cameraHierarchy( parentGroup )

        mc.undoInfo( openChunk = True )

        for obj in cams:
            # convert obj to pyObj
            currentObj = pm.PyNode(obj)

            # look the last parent
            while pm.listRelatives(currentObj.name(), p=True):
                preParent = currentObj
                currentObj = pm.listRelatives(currentObj.name(), p=True)[0]

            if currentObj.name() == parentGroup:
                continue

            elif currentObj.name() in exceptions:
                try:
                    pm.parent( preParent, parentGroup )
                except:
                    pass

            else:
                try:
                    pm.parent( currentObj, parentGroup )
                except:
                    pass

        mc.undoInfo( closeChunk = True )

    def cameraHierarchy_check( self, *args ):

        priority = args[0][0]
        parentGroup = args[0][1]

        cams = self.cameraHierarchy( parentGroup )

        if cams:
    
            state = 2 # Error state
            note = 'Error, the following cameras are out of hierarchy: \n ( {0} )'.format( cams )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the following cameras are out of hierarchy: \n ( {0} )'.format( cams )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def timelineOffset( self, offset = int ):

        # Check is there no shot nodes started before frame 1001.
        shotnode = pm.ls( type = 'shot')

        if not shotnode:
            mc.warning( 'Missing shot node in scene.' )
            return False
        
        noOffsetShots = []

        for sn in shotnode:
            sf = sn.startFrame.get()

            if sf < offset:
                noOffsetShots.append( sn )

        return noOffsetShots

    def timelineOffset_check( self, *args ):

        priority = args[0][0]
        offset = args[0][1]

        sn = self.timelineOffset( offset = offset )

        offsetSN = False

        if not sn:
            offsetSN = True

        if sn:
            
            state = 2 # Error state
            note = 'Error, the following shot node do not respect the offset {0}: ( {1} ) '.format( offset, sn )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Error, the following shot node do not respect the offset {0}: ( {1} ) '.format( offset, sn )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def timelineOffset_select( self, *args ):

        offset = args[0][1]

        sn = self.timelineOffset( offset = offset )
        pm.select( sn )

    def sceneCameras( self ):
        
        # List all cameras in scene
        allCameras = pm.ls( type='camera')
        # Default cameras
        defaultCams = ['persp', 'front', 'side', 'top']

        cams = [] # Filter cameras.

        # Remove default cameras.
        for c in allCameras:
            camera = c.getParent()
            if camera in defaultCams:
                pass
            else:
                cams.append(camera)

        # return list of scene cameras as PyNode objects.
        return cams

    def nameConvention( self, node = None, prefix = ''):

        nodeName = node.name()

        nodeNameSplit = nodeName.split('_')

        # Check sufix 
        if not nodeName.startswith( prefix ):
            return node

        # Check sufix, shot number 
        if not nodeNameSplit[-1].isdigit() or len( nodeNameSplit[ -1 ]) != 4:
            return node

        # Check name convention
        if not re.match('s[0-9][0-9]e[0-9][0-9]', nodeNameSplit[1]):
            return node

        # TODO check nameconvention split name [2] ( key ) 01wtv


    def cameraName( self, prefix = 'shotcam_' ):

        cams = self.sceneCameras()

        if not cams:
            mc.warning( 'Missing custome cameras in scene.')
            return None

        noNameCams = []

        for cam in cams:
            
            cam = self.nameConvention( node = cam, prefix = prefix )
            if cam:
                noNameCams.append( cam )
            # TODO check nameconvention split name [2] ( key ) 01wtv

        return noNameCams

    def cameraName_check( self, *args ):
        """
        Check camera name in scene.  name convention = prefix_s00e00_key_0000 
        

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param deformerType: args[0][1] , Type of deformers to check for.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        prefix = args[0][1]

        noNameCams = self.cameraName( prefix = prefix )

        if noNameCams:
    
            state = 2 # Error state
            note = 'Error, The follow cameras do not match the name convention, ( or there no cameras ): \n ( {0} )'.format( noNameCams )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning,The follow cameras do not match the name convention: ( or there no cameras ) \n ( {0} )'.format( noNameCams )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 
        
    def cameraName_select( self, *args ):
        
        prefix = args[0][1]
        noNameCams = self.cameraName( prefix = prefix )
        if not noNameCams:
            mc.warning( 'No cameras to select.' )
            return

        pm.select( noNameCams )

    def shotnodeName( self, prefix = 'shotnode_' ):

        shotnode = pm.ls( type = 'shot' )
        
        if not shotnode:
            return None
        
        noName = []

        for sn in shotnode:
            
            sn = self.nameConvention( node = sn, prefix = prefix )
            if sn:
                noName.append( sn )
            # TODO check nameconvention split name [2] ( key ) 01wtv

        return noName
        
    def shotnodeName_check( self, *args ):
        """
        Check camera name in scene.  name convention = prefix_s00e00_key_0000 
        

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param deformerType: args[0][1] , Type of deformers to check for.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        prefix = args[0][1]

        shotnodes = self.shotnodeName( prefix = prefix )

        if shotnodes:
    
            state = 2 # Error state
            note = 'Error, The follow shot node do not match the name convention, ( or there no shot node ): \n ( {0} )'.format( shotnodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning,The follow shot node do not match the name convention: ( or there no shot node ) \n ( {0} )'.format( shotnodes )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def shotnodeName_select( self, *args ):
        prefix = args[0][1]
        shotnode = self.shotnodeName( prefix = prefix )
        if not shotnode:
            mc.warning( 'No cameras to select.' )
            return

        pm.select( shotnode )  

    def shotCameraCongruence( self,  condition = 'prefix' ):
        '''
        Check if the shotnode have the correct camera assigned.
        '''

        shotnode = pm.ls( type = 'shot' )

        noMatch = []

        for sn in shotnode:
            
            snName = sn.name()
            shotNameId = snName.split('_')
            
            if condition == 'prefix':
                shotNameId = '_'.join( shotNameId[1:] )

            elif condition == 'sufix':
                shotNameId = '_'.join( shotNameId[0:-1] )

            cc = sn.currentCamera.get().name()
            
            if shotNameId not in cc:
                noMatch.append( sn )

        return noMatch

    def shotCameraCongruence_check( self, *args ):
        """
        Check for type of deformers exist in scene. 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param deformerType: args[0][1] , Type of deformers to check for.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        condition = args[0][1]

        noMatchNodes = self.shotCameraCongruence( condition )

        if noMatchNodes:
    
            state = 2 # Error state
            note = 'Error, the camera shotnode relationship are not congruents: \n ( {0} )'.format( noMatchNodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the camera shotnode relationship are not congruents: \n ( {0} )'.format( noMatchNodes )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def shotCameraCongruence_select( self, *args ):

        condition = args[0][1]
        noMatchNodes = self.shotCameraCongruence( condition )
        pm.select( noMatchNodes )
        
    def shotCameraCongruence_fix( self, *args ):

        condition = args[0][1]

        noMatchNodes = self.shotCameraCongruence( condition )

        for shotnode in noMatchNodes:
            
            snName = shotnode.name()
            shotNameId = snName.split('_')
            shotNameId = '_'.join( shotNameId[1:] )

            if pm.objExists( 'shotcam_' + shotNameId ):
                pm.shot( shotnode, e = True, cc = ('shotcam_' + shotNameId) )

    def shotNodeScale( self, *args ):

        shotnode = pm.ls( type = 'shot' )

        if not shotnode:
            return

        scaleNodes = []

        for sn in shotnode:
            if sn.scale.get() != 1.0:
                scaleNodes.append( sn )

        return scaleNodes

    def shotNodeScale_check( self, *args ):
        """
        Check for type of deformers exist in scene. 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param deformerType: args[0][1] , Type of deformers to check for.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]

        scalenNodes = self.shotNodeScale( )

        if scalenNodes:
    
            state = 2 # Error state
            note = 'Error, the scale of some nodes is different from 1 :  \n ( {0} )'.format( scalenNodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the scale of some nodes is different from 1 :  \n ( {0} )'.format( scalenNodes )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def shotNodeScale_select( self, *args ):
        scaleNodes = self.shotNodeScale()
        pm.select( scaleNodes )

    def singleAudioTrack( self, *args ):
        
        audio = pm.ls( type = 'audio' )

        if not audio:
            return False
        elif len( audio ) != 1:
            return False
        
        return audio

    def singleAudioTrack_check( self, *args ):

        priority = args[0][0]

        audio = self.singleAudioTrack()

        if audio == False :
    
            state = 2 # Error state
            note = 'Error, there no audio or is more than one audio in the scene :  \n ( {0} )'.format( audio )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning,  there  no audio or is more than one audio in the scene :  \n ( {0} )'.format( audio )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def singleAudioTrack_select( self, *args ):
        
        audio = pm.ls( type = 'audio' )
        pm.select( audio )

    def checkAudioOffset( self, offset = int ):

        audio = pm.ls( type = 'audio')
        
        if audio[0].offset.get() == offset:
            return True
        
        return False

    def checkAudioOffset_check( self, *args ):

        priority = args[0][0]
        offset = args[0][1]

        audio = self.checkAudioOffset( offset )

        if audio == False :
    
            state = 2 # Error state
            note = 'Error, verify audio offset'

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, verify audio offset'

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def checkAudioOffset_fix( self, *args ):
        offset = args[0][1]

        audio = pm.ls( type = 'audio')[0]
        audio.offset.set( offset )

    def checkAudioOffset_select( self, *args ):

        audio = pm.ls( type = 'audio')[0]
        pm.select( audio )

    def checkNamespace( self, *args ):
        '''
        Check is there no capital latter on the namespace
        '''

        mc.namespace(setNamespace=':')
        namespaces = mc.namespaceInfo(listOnlyNamespaces=True, recurse=True)

        # Remove default namespace 
        filterNS = []
        for ns in namespaces:
            if ns in ['UI','shared']:
                pass
            else:
                filterNS.append( ns )
        
        # LowerCase
        lowercaseNS = []
        for ns in filterNS:
            r = re.findall('([A-Z])', ns )    
            if r:
                lowercaseNS.append( ns )

        return lowercaseNS

    def checkNamespace_check( self, *args ):

        priority = args[0][0]

        ns = self.checkNamespace(  )

        if ns:
    
            state = 2 # Error state
            note = 'Error, The follow namespace containe upper cases. \n {0}'.format( ns )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, The follow namespace containe upper cases. \n {0}'.format( ns )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def emptyGroupsLayout( self, exceptions = [] ):
        """
        This function find all the transforms nodes those not have children in they hierarchy.

        :return: List of empty transforms nodes.
        :rtype: string[]
        """

        nodes = mc.ls( type='transform' )

        # Remove exceptions 
        filterGrps = []
        for n in nodes:
            if n in exceptions:
                pass
            else:
                filterGrps.append( n )

        emptyNodes = []

        for n in filterGrps:
            if mc.listRelatives(n, ad=True):
                pass
            else:
                if mc.objectType( n )  == 'transform':
                    emptyNodes.append(n)

        return emptyNodes

    def emptyGroupsLayout_fix( self, *args ):
        exceptions = args[0][1]
        emptyNodes = self.emptyGroupsLayout( exceptions )

        mc.undoInfo( openChunk = True )
        try:
            mc.delete( emptyNodes )
        except:
            pass
        mc.undoInfo( closeChunk = True )

    def emptyGroupsLayout_select( self, *args ):
        exceptions = args[0][1]
        emptyNodes = self.emptyGroupsLayout( exceptions )
        pm.select( emptyNodes )

    def emptyGroupsLayout_check( self, *args ):

        priority = args[0][0]
        exceptions = args[0][1]

        emptyNodes = self.emptyGroupsLayout( exceptions )

        if emptyNodes:
    
            state = 2 # Error state
            note = 'Error, the follow nodes are empty:  \n ( {0} )'.format( emptyNodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the follow nodes are empty:  \n ( {0} )'.format( emptyNodes )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def camSpeed( self, *args ):
        pass

    def camSpeed_check( self, *args ):
        pass

    def camSpeed_select( self, *args ):
        pass

    def extraKeyframes( self, *args ):
        pass

    def sceneConstrain( self, allowedGrp = [ 'Camera', 'Temp' ] ):
        """
     
        :param args: ( *, [ priority, deformers type ] )
        :return: List of deformers names in scene.
        :rtype: string[]
        """

        # List constrain type and motion path nodes 
        const = pm.ls( type = 'constraint')
        motionPath = pm.ls( type = 'motionPath' )

        sceneConst = const + motionPath

        illegalConst = [] # Illegal constrain list 

        for c in sceneConst: # For constraint in scene constraint.

            relatedNodes = pm.listConnections( c ) # Get constraint node related nodes.
            relatedNodes = set(relatedNodes) 
            
            # If a related node are gruped under not allowed constraint group add it to illigalConst list. 
            for rNode in relatedNodes: 
                if pm.objectType( rNode ) == 'transform':
                    
                    currentObj = rNode

                    # Find the biggest parent 
                    while pm.listRelatives(currentObj.name(), p=True):
                        currentObj = pm.listRelatives(currentObj.name(), p=True)[0]
                    
                    if not currentObj in allowedGrp:
                        illegalConst.append( c )
                        continue
                
        illegalConst = set( illegalConst )

        return illegalConst
                
    def sceneConstrain_select( self, *args ):

        constraints = self.sceneConstrain( args[0][1] )
        pm.select( constraints )

    def sceneConstrain_check( self, *args ):

        priority = args[0][0]
        allowedGrp = args[0][1]

        constrain = self.sceneConstrain( allowedGrp )

        if constrain:
    
            state = 2 # Error state
            note = 'Error, the scene contains illegal constrain:  \n ( {0} )'.format( constrain )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the scene contains illegal constrain:  \n ( {0} )'.format( constrain )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def layoutHierarchy( self, allowedAssemblies = [] ):
        
        assemblies = pm.ls( assemblies = True )

        # Remove default assemblie nodes 

        for x in ['persp','top', 'side', 'front' ]:
            try:
                assemblies.remove(x)
            except:
                pass

        noGrouped = []

        for x in assemblies:
            if not x in allowedAssemblies:
                noGrouped.append( x )

        return noGrouped

    def layoutHierarchy_select( self, *args ):
        
        noGrp = self.layoutHierarchy( args[0][1] )
        pm.select( noGrp )

    def layoutHierarchy_check( self, *args ):

        priority = args[0][0]
        allowedGrps = args[0][1]
        noGrp = self.layoutHierarchy( allowedGrps )

        if noGrp:
    
            state = 2 # Error state
            note = 'Error, the following nodes are out of group: \n ( {0} )'.format( noGrp )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the following nodes are out of group: \n ( {0} )'.format( noGrp )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 


