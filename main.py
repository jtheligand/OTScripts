import panel as pn
import param
from templates import plate_consolidation, serial_dilution, plate_workup

pn.config.notifications = True

class opentrons_generator(param.Parameterized):
    workup_selector = param.Selector(objects=['','Workup plates', 'Consolidate plates', 'Serial dilute HTE plates'])
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
    
    ready = None

    #pn.widgets.IntInput.from_param(self['plate_final_vol'], value=2*self.plate_initial_vol, start = self.plate_initial_vol, end=800)
    @param.depends('workup_selector', 'reload_button', watch=True)
    def update_view(self):
        if self.workup_selector == 'Workup plates':
            self.param.max_plates.objects = [1,2,3]
        elif self.workup_selector == 'Serial dilute HTE plates':
            self.param.max_plates.objects = [1]
        elif self.workup_selector == 'Consolidate plates':
            self.param.max_plates.objects = [1,2,3,4]
        else:
            self.param.max_plates.objects = [1]

    @param.depends('file_download', watch = True)
    def generate_values(self):
        self.dilution_vol = self.plate_final_vol - self.plate_initial_vol
        self.analyt_vol = self.final_vol - self.aliquot_vol
        self.ready = True
        pn.state.notifications.success('File generated!')

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
        
    
    @param.depends('file_download', 'reload_button')
    def generate_file(self):
        if self.ready:
            if self.workup_selector == 'Workup plates':
                #return self.dilution_vol
                with open('outputs/'+self.experiment_no+'.py', 'w') as file:
                    file.write(plate_workup.render(plate_dilution_vol = self.dilution_vol, 
                                           aliquot_vol = self.aliquot_vol, 
                                          analytical_dilution_vol = self.analyt_vol,
                                          number_plates = self.max_plates))
            elif self.workup_selector == 'Serial dilute HTE plates':
                with open('outputs/'+self.experiment_no+'.py', 'w') as file:
                    file.write(plate_workup.render(plate_dilution_vol = self.dilution_vol, 
                                           aliquot_vol = self.aliquot_vol, 
                                          analytical_dilution_vol = self.analyt_vol,
                                          number_plates = self.max_plates))
            elif self.workup_selector == 'Consolidate plates':
                return 'consolidate'
            else:
                return 'Missing input'
        else:
            return 'no'

    def view(self):
        self.center = pn.WidgetBox(
            pn.widgets.TextInput.from_param(self.param['experiment_no'], width = 400,
                                            placeholder = 'JRS-2023-123', 
                                            name = 'Experiment number'),
            pn.widgets.Select.from_param(self.param['workup_selector'], name='Workup type', width = 400),
            pn.widgets.DiscreteSlider.from_param(self.param['max_plates'], name='Number of plates', width = 400),
            pn.Row(
                pn.widgets.IntInput.from_param(self.param['plate_initial_vol'], 
                                               start=25, end = 500, step = 25, width = 190,
                                               name = 'Initial plate volume (µL)'),
                pn.widgets.IntInput.from_param(self.param['plate_final_vol'], 
                                               start = 25, end = 800, step = 25, width = 190,
                                              name = 'Final plate volume (µL)')
            ),
            pn.Row(
                pn.widgets.IntInput.from_param(self.param['aliquot_vol'], 
                                               start = 20, end = 200, step = 10, width = 190,
                                              name = 'Aliquot volume (µL)'),
                pn.widgets.IntInput.from_param(self.param['final_vol'], 
                                               start = 400, end = 600, step = 50, width = 190,
                                              name = 'Final analytical sample vol (µL)')
            ),
            pn.Accordion(('Serial dilution parameters',
                          pn.Column(
                          pn.Row(
                                pn.widgets.IntInput.from_param(self.param['second_aliquot_vol'],
                                                               start = 20, end = 200, step = 5, width= 150,
                                                               name = '2nd aliquot volume (µL)'),
                                  pn.widgets.IntInput.from_param(self.param['second_final_vol'],
                                                                 start = 400, end = 600, step = 50, width = 220,
                                                                 name = 'Final vol. 2nd analytical plate (µL)')
                          ),
                          pn.layout.Divider(),
                          pn.Row(
                                pn.widgets.IntInput.from_param(self.param['third_aliquot_vol'],
                                                               start = 20, end = 200, step = 5, width = 150,
                                                               name = '3rd aliquot volume (µL)'),
                              pn.widgets.IntInput.from_param(self.param['third_final_vol'],
                                                             start = 400, end = 600, step = 50, width = 220,
                                                             name = 'Final vol. 3rd analytical plate (µL)')

                          ))), width = 420),
            pn.widgets.Button.from_param(self.param['file_download'], button_type = 'primary', width = 410),
            pn.widgets.Button.from_param(self.param['reload_button'], width = 410)
            )
        return pn.template.VanillaTemplate(
                site = 'UD HTE Center', 
                title = 'Opentrons Workup Script Generator',
                main = pn.Row(self.center, self.generate_file),
                header_background = '#376795', logo='icon.png').servable()

opentrons_generator().view()

