// File: bluejay_data.v
// Generated by MyHDL 0.11
// Date: Wed Apr  8 13:30:09 2020


`timescale 1ns/10ps

module bluejay_data (
    fpga_clk,
    reset_all,
    next_frame_rdy,
    fifo_data_out,
    line_of_data_available,
    fifo_empty,
    get_next_word,
    data_o,
    sync_o,
    valid_o,
    update_o,
    invert_o
);
// Peripheral to clock data out to a Bluejay SLM's Data Interface
// 
// I/O pins:
// --------
// Control:
// fpga_clk                : 100MHz input clock
// reset_all               : Reset line
// next_frame_rdy          : Signal line to indicate that we want to start outputting a new frame
// Read-Side:
// fifo_data_out           : 32-bit input data to be shown on SLM
// line_of_data_available  : line to indicate that a new line of data is available, active-high for 1 cycle
// fifo_empty              : flag to indicate whether or not the FIFO is empty
// get_next_word           : line to pull next data word out of fifo 
// Write-Side:
// data_o                  : 32-bit output line to data interface on Bluejay SLM
// sync_o                  : Synchronisation line on Bluejay SLM, used to control which address we are writing to
// valid_o                 : Hold high while writing out a line
// update_o                : Used to assert when a Buffer Switch shall take place
// invert_o                : Used to enable DC_Balancing

input fpga_clk;
input reset_all;
input next_frame_rdy;
input [31:0] fifo_data_out;
input line_of_data_available;
input fifo_empty;
output get_next_word;
reg get_next_word;
output [31:0] data_o;
reg [31:0] data_o;
output sync_o;
reg sync_o;
output valid_o;
reg valid_o;
output update_o;
reg update_o;
input invert_o;

reg [10:0] v_counter;
reg [7:0] h_counter;
reg [2:0] state;
reg [7:0] state_timeout_counter;
reg get_next_word_cmd;
reg data_output_active_cmd;



always @(posedge fpga_clk) begin: BLUEJAY_DATA_UPDATE
    sync_o <= 1'b0;
    valid_o <= valid_o;
    update_o <= 1'b0;
    case (state)
        3'b000: begin
            if (((line_of_data_available == 1'b1) && (v_counter >= 0))) begin
                state <= 3'b001;
                get_next_word_cmd <= 1'b1;
            end
        end
        3'b001: begin
            h_counter <= 40;
            valid_o <= 1'b1;
            data_output_active_cmd <= 1'b1;
            state <= 3'b010;
        end
        3'b010: begin
            get_next_word_cmd <= 1'b1;
            state <= 3'b010;
            h_counter <= (h_counter - 1);
            valid_o <= 1'b1;
            if ((h_counter == (0 + 1))) begin
                state <= 3'b011;
                get_next_word_cmd <= 1'b0;
                valid_o <= 1'b0;
                h_counter <= 0;
                data_output_active_cmd <= 1'b0;
                state_timeout_counter <= 4;
            end
        end
        default: begin
            case (state)
                3'b011: begin
                    state_timeout_counter <= (state_timeout_counter - 1);
                    if ((state_timeout_counter == 1)) begin
                        state_timeout_counter <= 0;
                        v_counter <= (v_counter - 1);
                        if ((v_counter == 1)) begin
                            state <= 3'b100;
                            state_timeout_counter <= 12;
                        end
                        else begin
                            state <= 3'b000;
                        end
                    end
                end
                3'b100: begin
                    state_timeout_counter <= (state_timeout_counter - 1);
                    if ((state_timeout_counter == (0 + 1))) begin
                        state_timeout_counter <= 48;
                        state <= 3'b101;
                    end
                end
                3'b101: begin
                    update_o <= 1'b1;
                    state_timeout_counter <= (state_timeout_counter - 1);
                    if ((state_timeout_counter == (0 + 1))) begin
                        state_timeout_counter <= 0;
                        state <= 3'b000;
                    end
                end
            endcase
        end
    endcase
    if ((next_frame_rdy == 1'b1)) begin
        v_counter <= 4;
    end
    if ((reset_all == 1'b1)) begin
        data_output_active_cmd <= 1'b0;
        sync_o <= 1'b0;
        valid_o <= 1'b0;
        update_o <= 1'b0;
        h_counter <= 0;
        v_counter <= 0;
        state <= 3'b000;
    end
end


always @(fifo_empty, get_next_word_cmd) begin: BLUEJAY_DATA_CHECK_FIFO_NOT_EMPTY
    if (((get_next_word_cmd == 1'b1) && (fifo_empty == 1'b0))) begin
        get_next_word = 1'b1;
    end
    else begin
        get_next_word = 1'b0;
    end
end


always @(data_output_active_cmd, fifo_data_out) begin: BLUEJAY_DATA_OUTPUT_CONNECT
    if (data_output_active_cmd) begin
        data_o = fifo_data_out;
    end
    else begin
        data_o = 0;
    end
end

endmodule
