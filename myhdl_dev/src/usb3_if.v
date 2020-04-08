// File: usb3_if.v
// Generated by MyHDL 0.11
// Date: Wed Apr  8 10:55:29 2020


`timescale 1ns/10ps

module usb3_if (
    ftdi_clk,
    FR_RXF,
    FT_OE,
    FT_RD,
    usb3_data_in,
    write_to_dc32_fifo,
    dc32_fifo_data_in,
    dc32_fifo_is_full
);
// Ports
// I/O pins:
// --------
// USB-Fifo Side:
// ftdi_clk                : 100MHz input clock from USB Chip to synchronise with reading from FT601 32-bit FIFOs
// FR_RXF                  : RXF_N tells us if data is available on the USB3 Chip and is an input
// FT_OE                   : OE_N is an active low output signal to tell the USB3 Chip that the FPGA is the bus master while asserted
// FT_RD                   : RD_N is an active low output signal to tell that USB3 Chip that data is being read (ie: it is the RD signal for the USB3 FIFO)
// usb3_data_in            : 32-bit wide Data lines from the FT601
// FIFO-side:
// write_to_dc32_fifo      : Signal to write to the interfacing FIFO
// dc32_fifo_data_in       : Data which shall go into 32-bit 
// dc_32_fifo_is_full      : Goes high when there are at least 40 lines of data available in the internal FIFO

input ftdi_clk;
input FR_RXF;
output FT_OE;
wire FT_OE;
output FT_RD;
wire FT_RD;
input [31:0] usb3_data_in;
output write_to_dc32_fifo;
reg write_to_dc32_fifo;
output [31:0] dc32_fifo_data_in;
reg [31:0] dc32_fifo_data_in;
input dc32_fifo_is_full;

reg RD_N;
wire RXF_N;
reg OE_N;




assign RXF_N = (!FR_RXF);
assign FT_OE = (!OE_N);
assign FT_RD = (!RD_N);


always @(negedge ftdi_clk) begin: USB3_IF_USB3_READOUT_SEQ_LOGIC
    if (((RXF_N == 1'b0) || (dc32_fifo_is_full == 1'b1))) begin
        OE_N <= 1'b0;
        RD_N <= 1'b0;
    end
    else if (((RXF_N == 1'b1) && (OE_N == 1'b0) && (dc32_fifo_is_full == 1'b0))) begin
        OE_N <= 1'b1;
        RD_N <= 1'b0;
    end
    else if (((RXF_N == 1'b1) && (OE_N == 1'b1) && (dc32_fifo_is_full == 1'b0))) begin
        OE_N <= 1'b1;
        RD_N <= 1'b1;
    end
end


always @(RD_N, RXF_N, usb3_data_in, dc32_fifo_is_full, OE_N) begin: USB3_IF_DC32_FIFO_ROUTING
    if (((RXF_N == 1'b1) && (OE_N == 1'b1) && (RD_N == 1'b1) && (dc32_fifo_is_full == 1'b0))) begin
        write_to_dc32_fifo = 1'b1;
    end
    else begin
        write_to_dc32_fifo = 1'b0;
    end
    dc32_fifo_data_in = usb3_data_in;
end

endmodule
