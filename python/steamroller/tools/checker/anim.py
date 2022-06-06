
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm


class Animation():

    def cleanLights_check( self, *args ):
        """
        This command indicate if there light objects in the scene.

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        """

        priority = args[0][0]

        # List all lights in scene.
        lights = mc.ls( type = mc.listNodeTypes( 'light' ) )

        if lights:
    
            state = 2 # Error state
            note = 'Error, scene contain light nodes. \n {0}'.format( lights )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, scene contain light nodes. \n {0}'.format( lights )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result    

    def cleanLights_fix( self, *args ):
        """
        Delete all light in the scene. 

        :param args: ( *, [ priority, omit namespace **bool** ] )
        """
        
        omitNS = args[0][1]

        # List all lights in scene.
        lights = pm.ls( type = mc.listNodeTypes( 'light' ) )

        # Delete lights. 
        mc.undoInfo( openChunk = True )

        for x in lights:

            # skip lights with namespace            
            if omitNS == True and ':' in x.name():
                continue

            else:
                try:
                    pm.lockNode( x, l = False ) # Unlock node
                    pm.delete( x.getParent() ) # Delete 
                except:
                    mc.warning( 'Skip delete: {}'.format( x ) )

        mc.undoInfo( closeChunk = True )

    def cleanLights_select( self, *args ):
        """
        This function select all lights in scene.
        """

        # List all lights in scene.
        lights = mc.ls( type = mc.listNodeTypes( 'light' ) )
        # Select 
        mc.select( lights )
        # Walk up to select transfrom. 
        mc.pickWalk( direction = 'up' ) 

    def animLayer_check( self, *args ):
        """
        This command indicate if there animation layers in the scene.

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        """

        priority = args[0][0]

        # List all lights in scene.
        animLayers = self.animLayer()

        if animLayers:
    
            state = 2 # Error state
            note = 'Error, scene contain animation layers. \n {0}'.format( animLayers )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, scene contain animation layers. \n {0}'.format( animLayers )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def animLayer( self, *args ):
        
        # List animation layers in scene.
        animLayer = mc.ls( type = 'animLayer' )

        # Remove base animation layer.
        try:
            animLayer.remove( 'BaseAnimation' )
        except:
            pass

        return animLayer

    def defaultRotationOrder_check( self, *args ):
        """
        This command indicates if rotate order whether it is at its default value or not.

        filterType: **tag** filter all objects tagged as control.
                    **prefix** filter objects by prefix.
                    **sufix** fitler objects by sufix.
                    **attr** filter objects who have specific attribute.

        :param args: args[0] = ( priority, filter type, prefix, sufix, attribute ) 

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: dict
        """

        priority = args[0][0]

        # Custome function parameteres. ( filter type, prefix, sufix, attr )
        filterType  = args[0][1][0]
        prefix      = args[0][1][1]
        sufix       = args[0][1][2]
        attr        = args[0][1][3]

        # List all lights in scene.
        ctrls = self.defaultRotationOrder( filterType = filterType, prefix = prefix, sufix = sufix, attr = attr)

        if ctrls:
    
            state = 2 # Error state
            note = 'Error, the following controls do not have their rotation order in default: \n {0}'.format( ctrls )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the following controls do not have their rotation order in default: \n {0}'.format( ctrls )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def defaultRotationOrder( self,  filterType = '', sufix = '', prefix = '', attr = '' ):
        
        # TODO's it is required to know the rig to know how to obtain the default value. ( could be custome attr, setting defalut etc.) 

        ctrls = self.filterControls( filterType = filterType, sufix = sufix, prefix = prefix, attrName = attr )

        modeCtrls = []

        for c in ctrls:
            
            try:
                defaultValue = mc.attributeQuery( 'rotateOrder' , node = c, listDefault = True ) [0]
                if defaultValue != mc.getAttr( '{0}.rotateOrder'.format( c ) ):
                    modeCtrls.append( c )
            except:
                mc.warning( 'Error trying to query default value: {0}.{1}'.format( c , attr ) )

        return modeCtrls

    def filterControls( self, filterType = '', sufix = '', prefix = '', attrName = '' ):
        """
        Filter all controls by specific condition

            tag: collect all objects tag as a controller 
            prefix: collect all objects with specific prefix.
            sufix: collect all objects with specific sufix.
            attr: collect all DAG objects with specific attribute.

        :param filterType: (str) tag, prefix, sufix
        :return: ist of all controls in the scene that are included within the conditions.
        :rtype: string[]
        """

        # Filter controls list.
        ctrls = []

        if filterType == 'tag':
            # If controls are taged as a "controls"
            ctrls  = mc.controller( ac = True, q = True)

        if filterType == 'sufix':
            # Filter controls by sufix.
            objs = mc.ls( type = 'transform' )

            for c in objs:
                if c.endswith( sufix ):
                    ctrls.append( c )

        if filterType == 'prefix':
            # Filter controls by sufix.
            objs = mc.ls( type = 'transform' )

            for c in objs:
                if c.statswith( prefix ):
                    ctrls.append( c )
        
        if filterType == 'attr':
            # Filter by attribute.
            objs = mc.ls( type = 'transform' )

            for c in objs:
                if mc.attributeQuery( attrName, n = c, ex = True ):
                    ctrls.append( c )
        
        return ctrls

    def defaultRotationOrder_select( self, *args ):
        """
        Select controls by the defined filter.
        """

        # Custome function parameteres. ( filter type, prefix, sufix, attr )
        filterType  = args[0][1][0]
        prefix  = args[0][1][1]
        sufix  = args[0][1][2]
        attr  = args[0][1][3]

        # List all lights in scene.
        ctrls = self.defaultRotationOrder( filterType = filterType, prefix = prefix, sufix = sufix, attr = attr)
        
        # Select controls.
        mc.select( ctrls )

    def defaultRotationOrder_fix( self, *args ):
        """
        This command set controls to default rotate order value.

        undo: Available.
        filterType: **tag** filter all objects tagged as control.
                    **prefix** filter objects by prefix.
                    **sufix** fitler objects by sufix.
                    **attr** filter objects who have specific attribute.

        :param args: args[0] = ( priority, filter type, prefix, sufix, attribute ) 
        """

        # Custome function parameteres. ( filter type, prefix, sufix, attr )
        filterType  = args[0][1][0]
        prefix  = args[0][1][1]
        sufix  = args[0][1][2]
        attr  = args[0][1][3]

        # List all lights in scene.
        ctrls = self.defaultRotationOrder( filterType = filterType, prefix = prefix, sufix = sufix, attr = attr)

        # Set control rotation order to default value.
        mc.undoInfo( openChunk = True )
        for c in ctrls:
            
            try:
                if filterType == 'attr':
                    # TODO Query attribute with default value. 
                    pass 
                else:
                    defaultValue = mc.attributeQuery( 'rotateOrder' , node = c, listDefault = True ) [0] # Query default value 

                mc.setAttr( '{0}.rotateOrder'.format( c ), defaultValue ) # Set value

            except:
                mc.warning( 'Error trying to query default value: {0}.{1}'.format( c , attr ) )

        mc.undoInfo( closeChunk = True )

    def auidoTrackAnim_check( self, *args ):
        """
        This command indicates if rotate order whether it is at its default value or not.


        :param args: args[0] = ( priority )

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: dict
        """

        priority = args[0][0]

        # List all lights in scene.
        audio = self.auidoTrackAnim()

        if not audio:
    
            # Check if audio exist in scene. 


            state = 2 # Error state
            note = 'Error, Missing audio track: \n {0}'.format( '' )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, Missing audio track: \n {0}'.format( '' )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 


    def auidoTrackAnim( self, offset = 0.0, cutIn = float, cutOut = float ):

        # List audio in scene.
        audios = mc.ls( type = 'audio' )

        if not audios:
            return

        # Check if audio start at same as shot 
        audioST = mc.getAttr( audios[0] + '.offset' )
        if audioST  == ( cutIn + offset ):
            pass


    # TODO's check audio path 
    def auidoTrackAnimPath( self, path = None ):    
        pass

    # Junk 
    def junkNodesAnim_check( self, *args ):
        """

        :param args: args[0] = ( priority )

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: dict
        """

        priority = args[0][0]

        # Identify junk functions.
        junk = self.findJunk()

        if junk:
    
            state = 2 # Error state
            note = 'Error, There are junk nodes in the scene: \n {0}'.format( junk )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, There are junk nodes in the scene: \n {0}'.format( junk )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 


    def findJunk( self ):

        # Junk nodes list 
        junkNodes = []

        # Anim bot nodes.
        animBot = self.animBotNode()
        
        # Image plane.


        return junkNodes

    def animBotNode( self ):
        """
        Query all animbot nodes in scene.
        :return: list of nodes relationed with animbot.
        :rtype: string[]
        """
        junkNodes = []

        # Anim bot node 
        animBotNodeName = 'animBot'
        if mc.objExists( animBotNodeName ):
            junkNodes.append( animBotNodeName )

        # Image plane 
        imgPlane = self.getImagePlane()
        if imgPlane:
            junkNodes.extend( imgPlane )



        return junkNodes

    def getImagePlane( self ):
        """
        Query all image plane node type in scene.
        :return: image plane nodes.
        :rtype: string[]
        """
        imgPlane = mc.ls( type = 'imagePlane' )
        return imgPlane



    def junkNodesAnim_select( self ):
        """
        Select junk nodes. 
        """
        junkNodes = self.findJunk()
        mc.select( junkNodes )

    def junkNodesAnim_fix( self ):
        """
        Delete junk nodes.
        undo: available.
        """
        junkNodes = self.findJunk()

        mc.undoInfo( openChunk = True )

        for x in junkNodes:
            mc.lockNode( x, l = False )
            try:
                mc.delete( x )
            except:
                mc.warning( 'Error trying to delete {0}'.format( x ) )

        mc.undoInfo( closeChunk = True )