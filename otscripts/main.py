import panel as pn
import param
from templates.templates import plate_consolidation, serial_dilution, plate_workup
#import templates

pn.config.notifications = True
directory = 'outputs/'

class opentrons_generator(param.Parameterized):
    workup_selector = param.Selector(objects=['','Workup plates', 'Consolidate plates', 'Serial dilute HTE plates'])
    group = param.Selector(objects = ['','Chain', 'DAW', 'Fox', 'Messina', 'MPW', 'JRS', 'ORD'])
    parent_plate = param.Selector(objects = {'Paradox 96-well plate': 'analyticalsales_96_tuberack_1000ul', 'Waters 700 µL plate': 'waters_96_wellplate_700ul'})
    daughter_plate = param.Selector(objects = {'Waters 700 µL plate': 'waters_96_wellplate_700ul', 'Paradox 96-well plate': 'analyticalsales_96_tuberack_1000ul'})
    plate_initial_vol = param.Integer(100)
    plate_final_vol = param.Integer(300)
    aliquot_vol = param.Integer(20)
    final_vol = param.Integer(400)
    second_aliquot_vol = param.Integer(20)
    second_final_vol = param.Integer(400)
    third_aliquot_vol = param.Integer(20)
    third_final_vol = param.Integer(400)
    number_plates = param.Integer()
    experiment_no = param.String()
    max_plates = param.Selector(objects = [1])
    file_download = param.Action(default = lambda x: x.param.trigger('file_download'), label = 'Generate file')
    status = param.String('nothing loaded')
    reload_button = param.Action(default = lambda x: x.param.trigger('reload_button'), label = 'Clear form')
    instructions = param.String()
    
    ready = None

    @param.depends('workup_selector', 'reload_button', watch=True)
    def update_view(self):
        if self.workup_selector == 'Workup plates':
            self.param.max_plates.objects = [1,2,3]
            self.param.max_plates = 1
        elif self.workup_selector == 'Serial dilute HTE plates':
            self.param.max_plates.objects = [1]
        elif self.workup_selector == 'Consolidate plates':
            self.param.max_plates.objects = [1,2,3,4]
            self.param.max_plates = 1
        else:
            self.param.max_plates.objects = [1]

    @param.depends('file_download', watch = True)
    def generate_values(self):
        if (self.experiment_no == '')|(self.workup_selector == '')|(self.group == ''):
            pn.state.notifications.warning('Experiment number, group, and workup type must not be blank')
        elif (self.max_plates > 3)&(self.workup_selector == 'Workup plates'):
            pn.state.notifications.warning('Number of plates is too large')
            pn.state.notifications.info('Slider value does not automatically update when switching protocol')
        else:
            self.dilution_vol = self.plate_final_vol - self.plate_initial_vol
            self.sec_analyt_vol = self.second_final_vol - self.second_aliquot_vol
            self.third_analyt_vol = self.third_final_vol - self.third_aliquot_vol
            if self.workup_selector == 'Consolidate plates':
                self.analyt_vol = self.final_vol - self.aliquot_vol * 4
                if (self.dilution_vol > 200)|(self.analyt_vol > 500):
                    pn.state.notifications.warning('Dilution volumes for HTE plates and analytical plate are too large')
                else:
                    self.ready = True
            else:
                self.analyt_vol = self.final_vol - self.aliquot_vol
                self.ready = True
                print(self.max_plates)
    
    
            

    @param.depends('reload_button', watch = True)
    def clear_form(self):
        self.ready = None
        self.plate_initial_vol = 100
        self.plate_final_vol = 300
        self.aliquot_vol = 20
        self.final_vol = 400
        self.second_aliquot_vol = 20
        self.second_final_vol = 400
        self.third_aliquot_vol = 20
        self.third_final_vol = 400
        self.workup_selector = ''
        self.experiment_no = ''
        self.group = ''
        pn.state.notifications.info('Form reset')
        
    
    @param.depends('file_download', 'reload_button', watch = True)
    def generate_file(self):
        if self.ready:
            
            print('ready')
            if self.workup_selector == 'Workup plates':
                #return self.dilution_vol
                with open(directory+self.group+"_"+self.experiment_no+'.py', 'w') as file:
                    file.write(plate_workup.render(plate_dilution_vol = self.dilution_vol, 
                                        aliquot_vol = self.aliquot_vol, 
                                        analytical_dilution_vol = self.analyt_vol,
                                        number_plates = self.max_plates,
                                        destination_plate = self.daughter_plate,
                                        source_plate = self.parent_plate))
            elif self.workup_selector == 'Serial dilute HTE plates':
                with open(directory+self.group+"_"+self.experiment_no+'.py', 'w') as file:
                    file.write(serial_dilution.render(plate_dilution_vol = self.dilution_vol, 
                                        first_aliquot_vol = self.aliquot_vol, 
                                        first_analytical_dilution_vol = self.analyt_vol,
                                        second_aliquot_vol = self.second_aliquot_vol,
                                        second_analytical_dilution_vol = self.sec_analyt_vol,
                                        third_aliquot_vol = self.third_aliquot_vol,
                                        third_analytical_dilution_vol = self.third_analyt_vol,
                                        destination_plate = self.daughter_plate,
                                        source_plate = self.parent_plate))
            elif self.workup_selector == 'Consolidate plates':
                with open(directory+self.group+"_"+self.experiment_no+'.py', 'w') as file:
                    file.write(plate_consolidation.render(plate_dilution_vol = self.dilution_vol,
                                        aliquot_vol = self.aliquot_vol,
                                        analytical_dilution_vol = self.analyt_vol,
                                        number_plates = self.max_plates,
                                        destination_plate = self.daughter_plate,
                                        source_plate = self.parent_plate))
            else:
                return 'Missing input'
            pn.state.notifications.success('Generated file {}!'.format(self.group+"_"+self.experiment_no+'.py'))
        #else:
        #    return 'no'
    
    @param.depends('workup_selector', 'max_plates', watch = True)
    def preview_img(self):
        if self.workup_selector == 'Workup plates':
            workup_imgs = {1:'imgs/workup_oneplate.PNG', 2:'imgs/workup_twoplates.PNG', 3:'imgs/workup_threeplates.PNG'}
            return workup_imgs[self.max_plates]
        elif self.workup_selector == 'Serial dilute HTE plates':
            return 'imgs/serialdilution.PNG'
        elif self.workup_selector == 'Consolidate plates':
            consolidate_imgs = {1:'imgs/consolidate_oneplate.PNG', 2:'imgs/consolidate_twoplates.PNG', 3:'imgs/consolidate_threeplates.PNG', 4:'imgs/consolidate_fourplates.PNG'}
            return consolidate_imgs[self.max_plates]
        else:
            return 'imgs/empty_deck.png'
    
    @param.depends('workup_selector', watch = True)
    def workup_description(self):
        if self.workup_selector == 'Workup plates':
            return """
                <p>This protocol will dilute up to 3 HTE plates and then transfer aliquots from each well into an analytical plate and dilute</p>
            """
        elif self.workup_selector == 'Serial dilute HTE plates':
            return """
                <p>This protocol will dilute your HTE plate and up to 3 analytical plates, then transfer aliquots from the parent into each daughter analytical plate, mixing along the way</p>
                <p>If you are running a serial dilution but do not need to do a tertiary dilution, then set the third aliquot vol and/or third final plate volume to 0</p>
            """
        elif self.workup_selector == 'Consolidate plates':
            return """
                <p>This protocol will consolidate four columns at a time into an analytical plate from up to four HTE plates</p>
            """
        else:
            return "Select a protocol in the sidebar to see its description and deck layout"

    @param.depends('workup_selector', watch = True)
    def instructions_text(self):
        if self.workup_selector == 'Workup plates':
            return """
            <ol>
                <li>Place your HTE plates and analytical plates on the deck as shown.</li>
                <li>Place full tipracks on the deck as shown.</li>
                <li>Empty the trash bag (if required) and replace with a fresh liner if damaged.</li>
                <li>Fill highlighted sectors of two 4-well reservoirs with <b>65 mL</b> of the solvent of your choice. </li>
                <li>Double-check that all plates and tipracks are sitting correctly on the deck.</li>
                <li>Upload your script from the folder on the server to the Opentrons app then follow the prompts in the app.</li>
                <li>When protocol is complete, remove the empty tipracks and your plates from the deck, throw away used tips, and dispose of excess dilution solvent in the organic waste.</li>
                <li>Leave empty reservoirs to dry on the drying rack.</li>
            </ol>
            """
        elif self.workup_selector == 'Serial dilute HTE plates':
            return """
            <ol>
                <li>Place your HTE plates and analytical plates on the deck as shown.</li>
                <li>Place full tipracks on the deck as shown.</li>
                <li>Empty the trash bag (if required) and replace with a fresh liner if damaged.</li>
                <li>Fill highlighted sectors of the 4-well reservoir with <b>65 mL</b> of the solvent of your choice. </li>
                <li>Double-check that all plates and tipracks are sitting correctly on the deck.</li>
                <li>Upload your script from the folder on the server to the Opentrons app then follow the prompts in the app.</li>
                <li>When protocol is complete, remove the empty tipracks and your plates from the deck, throw away used tips, and dispose of excess dilution solvent in the organic waste.</li>
                <li>Leave empty reservoir to dry on the drying rack.</li>
            </ol>
            """
        elif self.workup_selector == 'Consolidate plates':
            return """
            <ol>
                <li>Place your HTE plates and analytical plates on the deck as shown.</li>
                <li>Place full tipracks on the deck as shown.</li>
                <li>Empty the trash bag (if required) and replace with a fresh liner if damaged.</li>
                <li>Fill highlighted sectors of the 6-well reservoir with <b>40 mL</b> of the solvent of your choice. </li>
                <li>Double-check that all plates and tipracks are sitting correctly on the deck.</li>
                <li>Upload your script from the folder on the server to the Opentrons app then follow the prompts in the app.</li>
                <li>When protocol is complete, remove the empty tipracks and your plates from the deck, throw away used tips, and dispose of excess dilution solvent in the organic waste.</li>
                <li>Leave empty reservoir to dry on the drying rack.</li>
            </ol>
            """
        else:
            #print('cleared')
            return  "<p>Select a workup protocol to see its instructions</p>"
    
    
    
    @param.depends('file_download', 'reload_button','workup_selector', 'max_plates', watch = False)
    def instructions_view(self):
        return pn.Row(
            pn.Column(pn.pane.HTML("<h3>Deck layout:</h3>", margin = (0,10,0,10)),
                pn.pane.PNG(self.preview_img(), height=650, margin = (0,10,0,10))),
            pn.Column(
                pn.WidgetBox(
                pn.pane.HTML(
                """
                <h3>Instructions:</h3>
                <p>To get your script and instructions on protocol set-up, enter your experimental details in the left-hand box then select <b>Generate File</b>.</p>
                
                """), width=450),
                pn.WidgetBox(
                pn.pane.HTML("""
                <h3>Protocol description:</h3>
                {}
                <h3>Protocol directions:</h3>
                {}

                """.format(self.workup_description(),self.instructions_text())), width=450, height = 590)))
    #self.preview_img(), 
    
    def sidebar(self):
        controls = pn.Column(
            pn.Card(
                pn.Row(
                    pn.widgets.Select.from_param(self.param['group'], width = 160,margin = (0,10,0,10)),
                    pn.widgets.TextInput.from_param(self.param['experiment_no'], width = 200,
                                            placeholder = 'JRS-2023-123', 
                                            name = 'Experiment number',margin = (0,10,0,10))),
                pn.widgets.Select.from_param(self.param['workup_selector'], name='Workup type', width = 380),
                pn.widgets.DiscreteSlider.from_param(self.param['max_plates'], name='Number of plates', width = 380),
                pn.Row(
                    pn.widgets.Select.from_param(self.param['parent_plate'], width = 180, name = 'Parent plate format'),
                    pn.widgets.Select.from_param(self.param['daughter_plate'], width = 180, name = 'Daughter plate format')),
                title = 'Plate description', width = 400, margin=10),
            pn.Card(
                pn.Row(
                    pn.widgets.IntInput.from_param(self.param['plate_initial_vol'], 
                                               start=25, end = 500, step = 25, width = 160,
                                               name = 'Initial plate volume (µL)'),
                    pn.widgets.IntInput.from_param(self.param['plate_final_vol'], 
                                               start = 25, end = 800, step = 25, width = 200,
                                              name = 'Final plate volume (µL)')
                    ),
                pn.Row(
                    pn.widgets.IntInput.from_param(self.param['aliquot_vol'], 
                                               start = 20, end = 200, step = 10, width = 160,
                                              name = 'Aliquot volume (µL)'),
                    pn.widgets.IntInput.from_param(self.param['final_vol'], 
                                               start = 400, end = 600, step = 50, width = 200,
                                              name = 'Final analytical sample vol. (µL)')
                    ),
                title = 'Dilution parameters', width = 400, margin = 10),
            pn.Card(
                pn.Column(
                pn.Row(
                    pn.widgets.IntInput.from_param(self.param['second_aliquot_vol'],
                                                    start = 20, end = 200, step = 5, width= 160,
                                                    name = '2nd aliquot volume (µL)'),
                        pn.widgets.IntInput.from_param(self.param['second_final_vol'],
                                                    start = 400, end = 600, step = 50, width = 200,
                                                    name = 'Final vol. 2nd analytical plate (µL)')
                ),
                pn.layout.Divider(),
                pn.Row(
                    pn.widgets.IntInput.from_param(self.param['third_aliquot_vol'],
                                                    start = 0, end = 200, step = 5, width = 160,
                                                    name = '3rd aliquot volume (µL)'),
                    pn.widgets.IntInput.from_param(self.param['third_final_vol'],
                                                    start = 0, end = 600, step = 50, width = 200,
                                                    name = 'Final vol. 3rd analytical plate (µL)')
                )), title = 'Serial dilution parameters', width = 400, collapsed = True,
                margin=10),
            pn.widgets.Button.from_param(self.param['file_download'], button_type = 'primary', width = 400),
            pn.widgets.Button.from_param(self.param['reload_button'], width = 400))
        return controls
    
    def view(self):
        return pn.template.VanillaTemplate(
                site = 'UD HTE Center', 
                title = 'Opentrons Workup Script Generator',
                main = self.instructions_view,
                sidebar = self.sidebar(),
                sidebar_width = 430,
                header_background = '#528FAC', logo='imgs/icon.png').servable()

opentrons_generator().view()

