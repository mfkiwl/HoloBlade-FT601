# bluejay_data.py


import sys
import traceback

import myhdl
from myhdl import *

import test_fifo


period = 10 # clk frequency = 50 MHz

t_state = enum(
    'RESET',
    'IDLE',
    'SYNC_PULSE',
    'SYNC_BLANK',
    'LINE_OUT_IDLE',
    'LINE_OUT_ENTER',
    'LINE_OUT_DATA',
    'LINE_OUT_BLANK'
    )


@block
def bluejay_data(fpga_clk, start_clocking_frame_data, fifo_data_out, line_of_data_available, fifo_empty, get_next_word, data_o, sync, valid):


    """ Peripheral to clock data out to a Bluejay SLM's Data Interface

    I/O pins:
    --------
    Control:
    fpga_clk                   : 100MHz input clock
    start_clocking_frame_data: : line to tell the blue_data object to start clocking next frame of data from USB into SLM, note that this is high for 1-cycle and shall be generated by timing_controller straight after an UPDATE to minimise chance of frame tearing
    Read-Side:
    fifo_data_out              : 32-bit input data to be shown on SLM
    line_of_data_available     : line to indicate that a new line of data is available, active-high for 1 cycle
    fifo_empty                 : flag to indicate whether or not the FIFO is empty
    get_next_word              : line to pull next data word out of fifo 
    Write-Side:
    data_o                     : 32-bit output line to data interface on Bluejay SLM
    sync                       : Synchronisation line on Bluejay SLM, used to control which address we are writing to
    valid                      : Hold high while writing out a line

    """


    # Timing constants
    num_words_per_line = 40
    num_lines          = 1280
    end_of_sync_blank_cycles  = 3  # Need to blank for 3 cycles between Sync Low and Valid high (tSD from pg. 14 datasheet)
    end_of_line_blank_cycles  = 4  # Need to blank for 4 cycles between subsequent line writes (tBLANK from pg. 14 datasheet)

    # Signals
    end_of_image_reached    = Signal(False, delay=10)
    v_counter               = Signal(intbv(0)[11:])
    state_timeout_counter   = Signal(intbv(0)[8:])
    # get_next_word_cmd       = Signal(False)
    # data_output_active_cmd  = Signal(False)
    state                   = Signal(t_state.IDLE)

    # Combinational Logic to ensure that we only ever get data from FIFO when not empty
    # @always_comb
    # def check_fifo_not_empty():
    #     if (get_next_word_cmd==True) and (fifo_empty==False):
    #         get_next_word.next = True
    #     else:
    #         get_next_word.next = False

    # Combinational Logic to ensure that we simply output data straight from FIFO input and don't ahve to deal with 1-cycle delays
    # @always_comb
    # def output_connect():
    #     if(data_output_active_cmd):
    #         data_o.next = fifo_data_out
    #     elif(sync):
    #         data_o.next = 0x00000000 # We're always syncing to 0, first line in a frame
    #     else:
    #         data_o.next = 0x00000000


    @always(fpga_clk.negedge)
    def falling_edge_outputs():

        # DATA, VALID and SYNC must conform to the timing requirements outlined in pg. 15.
        # To meet these requirements, we clock the values out on the preceeding negedge using the appropriate state

        # Default is that these values are all False
        data_o.next        = 0x00000000
        valid.next         = False
        get_next_word.next = False
        sync.next          = False

        # Set outputs in appropriate states
        if state == t_state.SYNC_PULSE:     
            sync.next = True
        elif state == t_state.LINE_OUT_ENTER:  
            valid.next         = True   
            data_o.next        = fifo_data_out
            get_next_word.next = True
        elif state == t_state.LINE_OUT_DATA: 
            valid.next         = True   
            data_o.next        = fifo_data_out
            get_next_word.next = True



    @always(fpga_clk.posedge)
    def update():

        # Default Outputs
        # sync.next  = False
        # valid.next = False

        # Before we run our state machine, we check start_clocking_frame_data
        # This line is generated directly from the UPDATE line being de-asserted and shall be high for 1 clock cycle only
        # Hence, we simply reset the state of this machine every single time we see this to manage our state (it is easier to lose track of everything than it seems as its all driven by the USB timings and there are edge-cases)
        # Lets us recover the system super-deterministically on every frame update
        if(start_clocking_frame_data==True):
            # Move to reset state
            state.next = t_state.RESET
            # Explicitly reset all state and values
            # data_output_active_cmd.next = False
            # sync.next                   = False
            # valid.next                  = False
            v_counter.next              = num_lines

        else:
            # Now we can run our state machince
            ################################################
            ################ STATE MACHINE #################
            ################################################
            # Which state are we in?
            if state == t_state.RESET:
                # Single-cycle state the clock cycle after start_clocking_frame_data was asserted
                # If there is data available , start clocking it out, otherwise simply go IDLE until next buffer switch
                if line_of_data_available==True:
                    # We have data, go to SYNC_PULSE state, asserting SYNC to be read next cycle
                    # Note that we don't need to expliclty set the DATA lines for SYNC as the combinational logic for output_connect above shall handle this
                    state.next = t_state.SYNC_PULSE
                    # sync.next = True
                else:
                    # Just wait in IDLE for the next buffer switch
                    state.next = t_state.IDLE

            # We sit in IDLE until we get a start_clocking_frame_data command while simulataneously having lines of data to-read available
            elif state == t_state.IDLE:
                # Just sit in here doing nothing and waiting
                state.next = t_state.IDLE

            ###########################################
            ############## Sync States ################
            ###########################################
            elif state == t_state.SYNC_PULSE:     
                # SYNC line is high for a single cycle while clocking out address data, this state is just to make sure it is pulled low
                # sync.next = False
                # Auto transition to blanking post-pulse
                state_timeout_counter.next = end_of_sync_blank_cycles
                state.next = t_state.SYNC_BLANK

            elif state == t_state.SYNC_BLANK:     
                state_timeout_counter.next = state_timeout_counter - 1
                # Finished blanking?
                if state_timeout_counter == 1:
                    # Move onto clocking out data in LINE_OUT_ENTER
                    state.next = t_state.LINE_OUT_ENTER

            ###########################################
            #### Clocking out Lines of Data States ####
            ###########################################
            elif state == t_state.LINE_OUT_ENTER:     
                # Need this wait state when entering a line as it will take 1 cycle to start getting data from FIFO
                # Reset counter and Valid line so they will start in-sync with FIFO Data - we clock out 1 word per clock cycle so simply set timeout_counter to words_per_line
                state_timeout_counter.next = num_words_per_line        
                # valid.next = True
                # Command to get next word out of FIFO also has to happen 1-cycle earlier (makes sense as synched with VALID)
                # get_next_word.next = True
                # Need to flag to combinational logic that we are clocking out data
                # data_output_active_cmd.next = True
                # Auto transition to main Data Out State
                state.next = t_state.LINE_OUT_DATA

            elif state == t_state.LINE_OUT_DATA: 
                # Keep reading from FIFO and maintain state
                # get_next_word.next = True
                #  Keep timing how many words clocked out and keep Valid high
                state_timeout_counter.next = state_timeout_counter - 1
                # valid.next = True
                # Are we at end of line?
                if state_timeout_counter == 1:
                    # Yes, advance state machine to end of line with appropriate blanking timing
                    state_timeout_counter.next = end_of_line_blank_cycles
                    state.next = t_state.LINE_OUT_BLANK
                    # Not getting any more data from FIFO
                    # get_next_word.next = False
                    # End of line so pull Valid Low and no longer outputting data
                    # valid.next = False
                    # data_output_active_cmd.next = False

            elif state == t_state.LINE_OUT_BLANK:
                # Need to blank appropriate number of cycles between lines
                state_timeout_counter.next = state_timeout_counter - 1
                # End of Blank period for end of line?
                if state_timeout_counter == 1:
                    # Decrement our row count as we have just finished clocking out a line
                    v_counter.next = v_counter - 1
                    # Have we clocked out the entire image?
                    if v_counter == 1:
                        # Yes, all done and clocked all our data into SLM, go back to idle and wait for next frame
                        state.next = t_state.IDLE
                    else:
                        # No, go back to LINE_OUT_IDLE to continue clocking out more lines
                        state.next = t_state.LINE_OUT_IDLE

            elif state == t_state.LINE_OUT_IDLE:
                # In this state, we have already started clocking out lines but might have to wait for additional lines to come out of the USB
                # No timing requirements here, we are simply waiting until we are certain data is available
                if line_of_data_available==True:
                    # Move onto clocking out data in LINE_OUT_ENTER
                    state.next = t_state.LINE_OUT_ENTER

    return update, falling_edge_outputs












# # testbench
# @block
# def bluejay_data_tb():

#     # Signals for Bluejay Data Module
#     # Control
#     fpga_clk                  = Signal(False)
#     start_clocking_frame_data = Signal(False)
#     # Read-Side
#     fifo_data_out             = Signal(0)
#     line_of_data_available    = Signal(False)
#     fifo_empty                = Signal(False)
#     get_next_word             = Signal(False)
#     # Write-Side
#     bluejay_data_o = Signal(0)
#     sync           = Signal(False)
#     valid          = Signal(False)
#     # Inst our Bluejay Data Interface
#     bluejay_data_inst = bluejay_data(fpga_clk, start_clocking_frame_data, fifo_data_out, line_of_data_available, fifo_empty, get_next_word, bluejay_data_o, sync, valid)


#     # Inst our simulated FIFO
#     fifo_data_i = Signal(0)
#     we = Signal(False)
#     full = Signal(False)
#     empty = Signal(False)
#     # fifo_empty.next = not empty
#     dut = test_fifo.fifo2(fifo_data_out, fifo_data_i, get_next_word, we, empty, full, fpga_clk, maxFilling=2000000)

#     # Clock
#     PERIOD = 10 # 50 MHz
#     @always(delay(PERIOD))
#     def clkgen():
#         fpga_clk.next = not fpga_clk

#     # Invert the empty signal
#     @always_comb
#     def inv():
#         fifo_empty.next = not empty


    # # Load test data
    # @instance
    # def load_test_data():

    #     # Test Vector corresponds to a single line of data
    #     test_vector = [

    #         # 40 Words of Data
    #         0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000,
    #         0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000,
    #         0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000,
    #         0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0x00000000
    #     ]
    #     # Wait an initial period
    #     FULL_CLOCK_PERIOD = 2*PERIOD
    #     yield delay(FULL_CLOCK_PERIOD)
    #     # Reset
    #     yield fpga_clk.negedge
    #     # reset_all.next = True
    #     yield fpga_clk.posedge
    #     # reset_all.next = False
        
    #     # yield fpga_clk.negedge
    #     # start_clocking_frame_data.next = False
    #     # yield fpga_clk.posedge
    #     # Iterate through test vector
    #     for i in range(1280):

    #         # Wait 1us and then load another line
    #         yield delay(1000)

    #         # Load line
    #         for item in test_vector:
    #             yield fpga_clk.negedge
    #             # yield delay(10)
    #             fifo_data_i.next = item
    #             we.next = True
    #             # yield delay(10)
    #             yield fpga_clk.posedge
    #             # yield delay(1)
    #             we.next = False
    #             # yield delay(10)

    #         # Assert that we have reached end-of-line
    #         yield fpga_clk.negedge
    #         # yield delay(FULL_CLOCK_PERIOD)
    #         line_of_data_available.next = True
    #         yield fpga_clk.posedge
    #         line_of_data_available.next = False
    #         yield fpga_clk.negedge
    #         # yield delay()
    #         we.next = False

    #     # Wait another 10us then end simulation
    #     yield delay(10000)
    #     # End Simulation
    #     raise StopSimulation()

    # return instances()

# Generated Verilog
def bluejay_gen_verilog():

    # Signals for Bluejay Data Module
    # Control
    fpga_clk                  = Signal(False)
    start_clocking_frame_data = Signal(False)
    # Read-Side
    fifo_data_out             = Signal(intbv(0)[32:])
    line_of_data_available    = Signal(False)
    fifo_empty                = Signal(False)
    get_next_word             = Signal(False)
    # SLM-Side
    bluejay_data_o   = Signal(intbv(0)[32:])
    sync             = Signal(False)
    valid            = Signal(False)
    # Inst our Bluejay Data Interface
    bluejay_data_inst = bluejay_data(
        # Control
        fpga_clk,
        start_clocking_frame_data,
        # FPGA-side
        fifo_data_out,
        line_of_data_available,
        fifo_empty,
        get_next_word,
        # SLM-side
        bluejay_data_o,
        sync,
        valid,
    )

    # Convert
    bluejay_data_inst.convert(hdl='Verilog')


def main():

    # tb = bluejay_data_tb()
    # tb.config_sim(trace=True)
    # tb.run_sim(000)
    # tb.run_sim(5000000)

    # Just generate the code, above code was useful historically but now that it is so tightly coupled with timing_controller, bluejay_datapath_tb is a better test of both
    bluejay_gen_verilog()


if __name__ == '__main__':
    main()
           