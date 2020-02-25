# bluejay_data.py

from myhdl import *

import mock_fifo

period = 20 # clk frequency = 50 MHz

t_state = enum(
    'IDLE',
    'LINE_OUT_ENTER',
    'LINE_OUT_DATA',
    'LINE_OUT_IDLE'
    )

@block
def bluejay_data(clk_i, reset_i, state, data_i, next_line_rdy_i, fifo_empty_i, get_next_word_o, data_o, sync_o, valid_o, update_o, invert_o):

    """ Peripheral to clock data out to a Bluejay SLM's Data Interface

    I/O pins:
    --------
    Control:
    clk_i            : 50MHz input clock
    reset_i          : Reset line
    state            : Current state, output for debug in simulator
    Read-Side:
    data_i           : 32-bit input data to be shown on SLM
    next_line_rdy_i  : line to indicate that a new line of data is available, active-high for 1 cycle
    fifo_empty_i     : flag to indicate whether or not the FIFO is empty
    get_next_word_o  : line to pull next data word out of fifo 
    Write-Side:
    data_o           : 32-bit output line to data interface on Bluejay SLM
    sync_o           : Synchronisation line on Bluejay SLM, used to control which address we are writing to
    valid_o          : Hold high while writing out a line
    update_o         : Used to assert when a Buffer Switch shall take place
    invert_o         : Used to enable DC_Balancing

    """


    # Timing constants
    num_words_per_line = 3 #40
    num_lines = 2 #1280

    # Signals
    end_of_image_reached = Signal(False, delay=10)
    h_counter = Signal(intbv(0, max=num_words_per_line))
    v_counter = Signal(intbv(0, max=num_lines))
    get_next_word_cmd = Signal(False)
    # state = Signal(t_state.IDLE)
    # shiftReg = Signal(modbv(0)[50:])


    # @always(clk_i.negedge)
    # def clear():

    #     if state == (t_state.LINE_OUT_DATA or LINE_OUT_ENTER):
    #         get_next_word_o.next = get_next_word_o#True

    # Combinational Logic to ensure that we only ever get data from FIFO when not empty
    @always_comb
    def check_fifo_not_empty():
        if (get_next_word_cmd==True) and (fifo_empty_i==False):
            get_next_word_o.next = True
        else:
            get_next_word_o.next = False

    # Combinational Logic to ensure that we simply output data straight from FIFO input
    @always_comb
    def output_connect():
        data_o.next = data_i

    @always(clk_i.posedge)
    def update():

        # Default Outputs
        sync_o.next = False
        valid_o.next = valid_o
        # update_o.next = update_o
        # end_of_image_reached.next = False

        # Which state are we in?

        if state == t_state.IDLE:

            # When the next line is ready, transition to clocking out data
            if( next_line_rdy_i==True ):
                state.next = t_state.LINE_OUT_ENTER
                # Also clock out the first word from FIFO so ready to start outputting at next clock edge
                get_next_word_cmd.next = False
                # data_o.next = data_i


        elif state == t_state.LINE_OUT_ENTER:     
                   
            # Read from FIFO and Latch our data output
            # get_next_word_o.next = True
            # data_o.next = data_i
            state.next = t_state.LINE_OUT_DATA
            get_next_word_cmd.next = True

        elif state == t_state.LINE_OUT_DATA: 

            # if fifo_empty_i == True:
            #     state.next = t_state.IDLE
            #     get_next_word_cmd.next = False

            # else:

            # Read from FIFO and Latch our data output
            get_next_word_cmd.next = True
            # data_o.next = data_i
            state.next = t_state.LINE_OUT_DATA

        # elif state == t_state.LINE_OUT_IDLE:

        #     # Read from FIFO and Latch our data output
        #     get_next_word_o.next = True
        #     data_o.next = data_i
        #     state.next = t_state.LINE_OUT_DATA

            # # Are we at end of line?
            # if h_counter < num_words_per_line-1:
            #     # No, increment h_counter
            #     h_counter.next = h_counter + 1
            #     valid_o.next = True
            # else:

            #     # Yes, reset h_counter, and deassert sync_o
            #     h_counter.next = 0
            #     valid_o.next = False
            #     state.next = t_state.IDLE

                # # Are we at end of an image?
                # if v_counter < num_lines-1:
                #     # No, increment v_counter
                #     v_counter.next = v_counter + 1
                # else:
                #     # Yes, reset v_counter and assert update_o
                #     v_counter.next = 0
                #     # update_o.next = True
                #     end_of_image_reached.next = True
                #     # # Need to wait 16 cycles to pull update signal high, we wait 20
                #     # wait_time_ns = 16*period
                #     # yield delay(wait_time_ns)
                #     # # Need to hold for 2.5 ns minimum, we wait 5ns
                #     # yield delay(5)

        # print(h_counter, v_counter)


        # # Update Line Check - Used to control the timing of update_o signal
        # if( end_of_image_reached==True ):
        #     update_o.next = True
        #     end_of_image_reached.next = False
        # else:
        #     update_o.next = False

        # Reset Check
        if( reset_i==True ):
            # Explicitly clear all outputs
            data_o.next = intbv(0)[32:]
            sync_o.next = False
            valid_o.next = False
            update_o.next = False
            h_counter.next = 0
            v_counter.next = 0
            state.next     = t_state.IDLE


    


    # # Timing Constraints for UPDATE Line
    # @always(end_of_image_reached.posedge)
    # def update_signal_timing():
    #     update_o.next = True

    # @instance
    # def update_signal_timing():

    #     while True:
    #         if end_of_image_reached==True:
    #             # Need to wait 16 cycles to pull update signal high, we wait 20
    #             wait_time_ns = 16*period
    #             yield delay(wait_time_ns)
    #             update_o.next = True
    #             # Need to hold for 2.5 ns minimum, we wait 5ns
    #             yield delay(5)
    #             update_o.next = False

    return update, check_fifo_not_empty, output_connect












# testbench
@block
def bluejay_data_tb():

    # Signals for Bluejay Data Module
    # Control
    clk_i = Signal(False)
    reset_i = Signal(False)
    state = Signal(t_state.IDLE)
    # Read-Side
    data_i = Signal((intbv(0)[32:]))
    next_line_rdy_i = Signal(False)
    fifo_empty_i    = Signal(False)
    get_next_word_o = Signal(False)
    # Write-Side
    data_o = Signal((intbv(0)[32:]))
    sync_o = Signal(False)
    valid_o = Signal(False)
    update_o = Signal(False)
    invert_o = Signal(False)

    # We also use a mocked FIFO for testing
    # Signals
    din = Signal((intbv(0)[32:]))
    we = Signal(False)
    full = Signal(False)
    # Inst
    mock_fifo_inst = mock_fifo.fifo2(data_i, din, get_next_word_o, we, fifo_empty_i, full, clk_i, maxFilling=64)

    # Device under test for testing
    bluejay_data_inst = bluejay_data(clk_i, reset_i, state, data_i, next_line_rdy_i, fifo_empty_i, get_next_word_o, data_o, sync_o, valid_o, update_o, invert_o)

    # Clock
    PERIOD = 10 # 50 MHz
    @always(delay(PERIOD))
    def clkgen():
        clk_i.next = not clk_i

    # Timing Code, useful for clearing our Assert signals
    @always(clk_i.posedge)
    def timing():
        # data_i.next = data_i.next + 1
        # Clear Assert signals
        # if data_rdy_i==True:
        if(next_line_rdy_i==True):
            next_line_rdy_i.next = False
        if(reset_i==True):
            reset_i.next    = False

    # # Data Ready goes high for 1 cycle for latching output
    # @always(delay(100))
    # def data_rdy_assert():
    #     data_rdy_i.next = 1
    # Clear next cycle
    # @instance
    # def data_rdy_clear():
    #     while True:

    # Load test data
    @instance
    def load_test_data():

        # Test Vector corresponds to a single line of data
        test_vector = [
            intbv(0x11000000)[32:],
            intbv(0x21000000)[32:],
            intbv(0x31000000)[32:]
            # intbv(0x41000000)[32:],
            # intbv(0x51000000)[32:],
            # intbv(0x61000000)[32:],
            # intbv(0x71000000)[32:],
            # intbv(0x81000000)[32:],
            # intbv(0x91000000)[32:],
            # intbv(0xA1000000)[32:],
            # intbv(0x12000000)[32:],
            # intbv(0x22000000)[32:],
            # intbv(0x32000000)[32:],
            # intbv(0x42000000)[32:],
            # intbv(0x52000000)[32:],
            # intbv(0x62000000)[32:],
            # intbv(0x72000000)[32:],
            # intbv(0x82000000)[32:],
            # intbv(0x92000000)[32:],
            # intbv(0xA2000000)[32:],
            # intbv(0x12000000)[32:],
            # intbv(0x23000000)[32:],
            # intbv(0x33000000)[32:],
            # intbv(0x43000000)[32:],
            # intbv(0x53000000)[32:],
            # intbv(0x63000000)[32:],
            # intbv(0x73000000)[32:],
            # intbv(0x83000000)[32:],
            # intbv(0x93000000)[32:],
            # intbv(0xA3000000)[32:],
            # intbv(0x14000000)[32:],
            # intbv(0x24000000)[32:],
            # intbv(0x34000000)[32:],
            # intbv(0x44000000)[32:],
            # intbv(0x54000000)[32:],
            # intbv(0x64000000)[32:],
            # intbv(0x74000000)[32:],
            # intbv(0x84000000)[32:],
            # intbv(0x94000000)[32:],
            # intbv(0xA4000000)[32:]
        ]
        # Wait initial 1ms to represent a real-world offset we would see with an actual system due to settling times
        # SETTLING_TIME = 1
        # yield delay(20)
        # yield delay(1)
        # Reset
        reset_i.next = 1
        # Iterate through test vector
        while True:

            # Wait 500ms and then load another line
            yield delay(500)

            # Load line
            for item in test_vector:
                yield clk_i.negedge
                din.next = intbv(item)[32:]
                we.next = True
                yield clk_i.posedge
                yield delay(1)
                we.next = False

            # Assert that we have reached end-of-line
            yield clk_i.negedge
            next_line_rdy_i.next = True
            yield clk_i.posedge
            yield delay(1)
            we.next = False

    return mock_fifo_inst, bluejay_data_inst, clkgen, timing, load_test_data


# Simulation
def simulate():

    tb = bluejay_data_tb()
    tb.config_sim(trace=True)
    tb.run_sim(1300)


# Execution
simulate()