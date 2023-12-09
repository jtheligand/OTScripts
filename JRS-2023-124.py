from opentrons import protocol_api
metadata = {'author': 'Jessica Sampson'}

requirements = {
	"robotType": "OT-2",
	"apiLevel": "2.15"
}

def gen_vol_list(volume):
	steps = int(volume/200)
	step = 0
	dispense_vols = []
	while step < steps:
		dispense_vols.append(200)
		step += 1
	if volume % 200 > 0:
		dispense_vols.append(volume % 200)
	return dispense_vols

plate_dilution_vol = 200
plate_dilution_list = gen_vol_list(plate_dilution_vol)
aliquot_vol = 20
analytical_dilution_vol = 380
analytical_dilution_list = gen_vol_list(analytical_dilution_vol)
number_plates = 1

def run(protocol: protocol_api.ProtocolContext):
	#Pipette set-up and overall parameters
	tiprack_name = 'opentrons_96_tiprack_300ul'
	tip_name = 'p300_multi_gen2'
	tip_head_side = 'left'
	tiprack_1 = protocol.load_labware(tiprack_name, 10)
	tiprack_2 = protocol.load_labware(tiprack_name, 11)
	tiprack_4 = protocol.load_labware(tiprack_name, 9)
	p300 = protocol.load_instrument(tip_name, 
			tip_head_side, 
			tip_racks=[tiprack_1, tiprack_2, tiprack_4])
	p300.well_bottom_clearance.dispense = 20
	p300.well_bottom_clearance.aspirate = 2
	p300.flow_rate.dispense = 150
	aspirate_flow_rate = 50
	air_gap = 10

	#Reservoir parameters
	reservoir_name = 'analyticalsales_4_reservoir_72000ul'
	reservoir_location_1 = 7
	reservoir_location_2 = 8
	reservoir_1 = protocol.load_labware(reservoir_name, reservoir_location_1)
	reservoir_2 = protocol.load_labware(reservoir_name, reservoir_location_2)

	#Labware set-up
	destination_plate_name = 'waters_96_wellplate_700ul'
	source_plate_name = 'analyticalsales_96_tuberack_1000ul'
	destination_list = [protocol.load_labware(destination_plate_name, x+3) for x in range(1, number_plates+1)]
	source_list = [protocol.load_labware(source_plate_name, x) for x in range(1,number_plates+1)]
	
	#Pick up tip and pre-wet
	reservoir_position = 0
	reservoir = reservoir_1
	p300.pick_up_tip()
	#protocol.pause(str(plate_dilution_list))
	p300.flow_rate.aspirate = 2*aspirate_flow_rate
	p300.mix(3, 150, reservoir.rows()[0][reservoir_position])
	
	
	#Dilute the source plates
	for plate in source_list:
		for i in plate.rows()[0]:
			for vol in plate_dilution_list:
				reservoir_well = reservoir.rows()[0][reservoir_position]
				p300.flow_rate.aspirate = aspirate_flow_rate
				p300.aspirate(vol, reservoir_well)
				p300.move_to(reservoir_well.top(z=3), speed=25)
				p300.flow_rate.aspirate = aspirate_flow_rate/20
				p300.aspirate(air_gap)
				p300.dispense(vol+air_gap, i)
				p300.blow_out()
				p300.touch_tip(i, radius=0.75, v_offset=-2)
		reservoir_position += 1
	

	#Dilute the analytical plate
	reservoir_position = 0
	reservoir = reservoir_2
	for plate in destination_list:
		for i in plate.rows()[0]:
			for vol in analytical_dilution_list:
				reservoir_well = reservoir.rows()[0][reservoir_position]
				p300.flow_rate.aspirate = aspirate_flow_rate
				p300.aspirate(vol, reservoir_well)
				p300.move_to(reservoir_well.top(z=3), speed=25)
				p300.flow_rate.aspirate = aspirate_flow_rate/20
				p300.aspirate(air_gap)
				p300.dispense(vol+air_gap, i)
				p300.blow_out()
				p300.touch_tip(i, radius=0.75, v_offset=-2)
			p300.flow_rate.aspirate = 2*aspirate_flow_rate
		reservoir_position += 1
	#p300.drop_tip()

	#Mix parent plate then aliquot into destination plate
	#p300.well_bottom_clearance.aspirate = 2
	p300.well_bottom_clearance.dispense = 5
	for source, destination in zip(source_list, destination_list):
		for i,j in zip(source.rows()[0], destination.rows()[0]):
			if i == source_list[0].rows()[0][0]:
				pass
			else:
				p300.pick_up_tip()
			p300.flow_rate.aspirate = 2*aspirate_flow_rate
			p300.mix(6, 150, i)
			p300.flow_rate.aspirate = aspirate_flow_rate
			p300.aspirate(aliquot_vol)
			p300.move_to(i.top(z=5), speed=25)
			p300.flow_rate.aspirate = aspirate_flow_rate/20
			p300.aspirate(air_gap)
			p300.dispense(aliquot_vol+air_gap, j)
			p300.flow_rate.aspirate = 2*aspirate_flow_rate
			p300.mix(6, 150, j)
			p300.touch_tip(j, radius=0.75, v_offset=-2)
			p300.blow_out()
			p300.drop_tip()