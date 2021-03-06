// File: spi.v
// Generated by MyHDL 0.11
// Date: Mon Jun  1 19:24:16 2020


`timescale 1ns/10ps

module spi (
    i_clock,
    enable,
    i_reset,
    start_transfer,
    multi_byte_spi_trans_flag,
    busy,
    byte_recv,
    MOSI,
    MISO,
    CS,
    SCLK,
    Tx_Upper_Byte,
    Tx_Lower_Byte,
    Rx_Recv_Byte
);
// MyHDL implementation of our SPI Module
// 
// I/O pins:
// --------
// Control:
// i_clock                    : Clock to drive this module
// enable                     : Output reset line for all other modules
// i_reset                    :
// start_transfer             :
// multi_byte_spi_trans_flag  :
// Status                     :
// busy                       :
// byte_recv                  : Goes high for 1 cycle when a SPI transfer is complete and a byte is ready to be read. Shall go high multiple times for a multi-byte read
// SPI Outputs:
// MOSI                       :
// MISO                       :
// CS                         :
// SCLK                       :
// Data Lines:
//     Tx_Upper_Byte              : Typically used for register address
//     Tx_Lower_Byte              : Typically used to set data to a register
//     Rx_Recv_Byte               : Received Data Byte from SPI Transaction

input i_clock;
input enable;
input i_reset;
input start_transfer;
input multi_byte_spi_trans_flag;
output busy;
reg busy;
output byte_recv;
reg byte_recv;
output MOSI;
wire MOSI;
input MISO;
output CS;
reg CS;
output SCLK;
reg SCLK;
input [7:0] Tx_Upper_Byte;
input [7:0] Tx_Lower_Byte;
output [7:0] Rx_Recv_Byte;
reg [7:0] Rx_Recv_Byte;

reg [7:0] multi_byte_counter;
reg [9:0] counter;
reg [15:0] tx_shift_reg;
reg [3:0] state;
reg [15:0] rx_shift_reg;



always @(posedge i_clock) begin: SPI_FSM_UPDATE
    if ((i_reset == 1'b1)) begin
        state <= 4'b0000;
        counter <= 0;
        tx_shift_reg <= 0;
        rx_shift_reg <= 0;
    end
    else begin
        SCLK <= 1'b0;
        CS <= 1'b1;
        busy <= 1'b1;
        byte_recv <= 1'b0;
        case (state)
            4'b0000: begin
                busy <= 1'b0;
                if (((enable == 1'b1) && (start_transfer == 1'b1))) begin
                    tx_shift_reg <= {Tx_Upper_Byte, Tx_Lower_Byte};
                    if ((multi_byte_spi_trans_flag == 1'b0)) begin
                        state <= 4'b0001;
                    end
                    else begin
                        state <= 4'b0110;
                    end
                end
            end
            4'b0001: begin
                counter <= 256;
                state <= 4'b0010;
                CS <= 1'b0;
            end
            4'b0010: begin
                CS <= 1'b0;
                counter <= (counter - 1);
                if (((counter % 32) < 16)) begin
                    SCLK <= 1'b0;
                end
                else begin
                    SCLK <= 1'b1;
                end
                if (((counter % 32) == (32 - 1))) begin
                    rx_shift_reg <= {rx_shift_reg[15-1:0], MISO};
                end
                if (((counter % 32) == (16 - 1))) begin
                    tx_shift_reg <= {tx_shift_reg[15-1:0], 1'b0};
                end
                if ((counter == (0 + 1))) begin
                    counter <= 256;
                    state <= 4'b0011;
                end
            end
            4'b0011: begin
                CS <= 1'b0;
                counter <= (counter - 1);
                if (((counter % 32) > 16)) begin
                    SCLK <= 1'b1;
                end
                else begin
                    SCLK <= 1'b0;
                end
                if (((counter % 32) == (32 - 1))) begin
                    rx_shift_reg <= {rx_shift_reg[15-1:0], MISO};
                end
                if (((counter % 32) == (16 - 1))) begin
                    tx_shift_reg <= {tx_shift_reg[15-1:0], 1'b0};
                end
                if ((counter == (0 + 1))) begin
                    state <= 4'b0100;
                    CS <= 1'b1;
                end
            end
            4'b0100: begin
                Rx_Recv_Byte <= rx_shift_reg[8-1:0];
                state <= 4'b0101;
            end
            4'b0101: begin
                byte_recv <= 1'b1;
                busy <= 1'b0;
                state <= 4'b0000;
            end
            4'b0110: begin
                counter <= 256;
                state <= 4'b0111;
                CS <= 1'b0;
            end
            4'b0111: begin
                CS <= 1'b0;
                counter <= (counter - 1);
                if (((counter % 32) < 16)) begin
                    SCLK <= 1'b0;
                end
                else begin
                    SCLK <= 1'b1;
                end
                if (((counter % 32) == (32 - 1))) begin
                    rx_shift_reg <= {rx_shift_reg[15-1:0], MISO};
                end
                if (((counter % 32) == (16 - 1))) begin
                    tx_shift_reg <= {tx_shift_reg[15-1:0], 1'b0};
                end
                if ((counter == (0 + 1))) begin
                    counter <= 256;
                    state <= 4'b1000;
                    multi_byte_counter <= 160;
                end
            end
            4'b1000: begin
                CS <= 1'b0;
                counter <= (counter - 1);
                if (((counter % 32) > 16)) begin
                    SCLK <= 1'b1;
                end
                else begin
                    SCLK <= 1'b0;
                end
                if (((counter % 32) == (32 - 1))) begin
                    rx_shift_reg <= {rx_shift_reg[15-1:0], MISO};
                end
                if (((counter % 32) == (16 - 1))) begin
                    tx_shift_reg <= {tx_shift_reg[15-1:0], 1'b0};
                end
                if ((counter == (0 + 1))) begin
                    state <= 4'b1001;
                end
            end
            4'b1001: begin
                Rx_Recv_Byte <= rx_shift_reg[8-1:0];
                CS <= 1'b0;
                state <= 4'b1010;
            end
            4'b1010: begin
                byte_recv <= 1'b1;
                CS <= 1'b0;
                if ((multi_byte_counter == (0 + 1))) begin
                    state <= 4'b0000;
                    busy <= 1'b0;
                    CS <= 1'b1;
                end
                else begin
                    state <= 4'b1000;
                    counter <= 256;
                    multi_byte_counter <= (multi_byte_counter - 1);
                end
            end
        endcase
    end
end



assign MOSI = tx_shift_reg[15];

endmodule
