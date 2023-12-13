from opentrons import protocol_api
metadata = {'author': 'Jessica Sampson'}

requirements = {
	'robotType': 'OT-2',
	'apiLevel': '2.15'
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
number_plates = 1 #Must be 3 or less!

def run(protocol: protocol_api.ProtocolContext):
	#Pipette set-up and overall parameters
	tiprack_name = 'opentrons_96_tiprack_300ul'
	tip_name = 'p300_multi_gen2'
	tip_head_side = 'left'
	tiprack_1 = protocol.load_labware(tiprack_name, 10)
	tiprack_2 = protocol.load_labware(tiprack_name, 11)
	tiprack_3 = protocol.load_labware(tiprack_name, 7)
	tiprack_4 = protocol.load_labware(tiprack_name, 9)
	tiprack_5 = protocol.load_labware(tiprack_name, 6)
	p300 = protocol.load_instrument(tip_name, 
			tip_head_side, 
			tip_racks=[tiprack_1, tiprack_2, tiprack_3, tiprack_4])
	p300.well_bottom_clearance.dispense = 20
	p300.well_bottom_clearance.aspirate = 3
	p300.flow_rate.dispense = 150
	aspirate_flow_rate = 50
	air_gap = 10

	#Reservoir parameters
	reservoir_name = 'analyticalsales_6_reservoir_4700ul'
	reservoir_location = 8
	reservoir = protocol.load_labware(reservoir_name, reservoir_location)

	#Labware set-up
	destination_plate_name = 'waters_96_wellplate_700ul'
	source_plate_name = 'analyticalsales_96_tuberack_1000ul'
	destination_plate = protocol.load_labware(destination_plate_name, 5)
	source_list = [protocol.load_labware(source_plate_name, x) for x in range(1,number_plates+1)]
	
	#Pick up tip and pre-wet
	reservoir_position = 0
	analytical_position = 0
	plate_number = 0
	column_count = 0
	vol_position = 0
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
	
	p300.drop_tip()
	
	
	#Mix parent plate then aliquot into destination plate
	p300.well_bottom_clearance.aspirate = 5
	p300.well_bottom_clearance.dispense = 15
	for source in source_list:
		for i in source.rows()[0]:
			p300.pick_up_tip()
			p300.flow_rate.aspirate = 2*aspirate_flow_rate
			p300.mix(6, 150, i)
			p300.flow_rate.aspirate = aspirate_flow_rate
			p300.aspirate(aliquot_vol)
			p300.move_to(i.top(z=5), speed=25)
			p300.flow_rate.aspirate = aspirate_flow_rate/20
			p300.aspirate(air_gap)
			p300.dispense(aliquot_vol+air_gap, destination_plate.rows()[0][analytical_position])
			p300.touch_tip(destination_plate.rows()[0][analytical_position], radius=0.75, v_offset=-2)
			p300.blow_out()
			p300.drop_tip()
			column_count += 1
			if column_count % 4 == 0:
				analytical_position += 1
			else:
				pass
		plate_number += 1
	
	
	#Dilute and mix the analytical plate
	p300.well_bottom_clearance.aspirate = 3
	p300.well_bottom_clearance.dispense = 15
	for i in destination_plate.rows()[0]:
		for vol in analytical_dilution_list:
			reservoir_well = reservoir.rows()[0][reservoir_position]
			if vol_position == 0:
				p300.pick_up_tip()
				p300.flow_rate.aspirate = 2*aspirate_flow_rate
				p300.mix(3, 150, reservoir_well)
			else:
				pass
			p300.flow_rate.aspirate = aspirate_flow_rate
			p300.aspirate(vol, reservoir_well)
			p300.move_to(reservoir_well.top(z=3), speed=25)
			p300.flow_rate.aspirate = aspirate_flow_rate/20
			p300.aspirate(air_gap)
			p300.dispense(vol+air_gap, i)
			vol_position += 1
			if vol_position == len(analytical_dilution_list):
				p300.move_to(i.bottom(z=3))
				p300.flow_rate.aspirate = 2*aspirate_flow_rate
				p300.mix(6, 150, i)
				p300.blow_out()
				p300.touch_tip(i, radius=0.75, v_offset=-2)
				p300.drop_tip()
				vol_position = 0
			else:
				p300.blow_out()
				p300.touch_tip(i, radius=0.75, v_offset=-2)
		if i == destination_plate.rows()[0][5]:
			reservoir_position += 1
		else:
			pass