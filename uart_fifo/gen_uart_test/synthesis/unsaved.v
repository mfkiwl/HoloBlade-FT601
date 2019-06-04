// unsaved.v

// Generated using ACDS version 18.1 625

`timescale 1 ps / 1 ps
module unsaved (
		input  wire       clk_clk,                                  //                                clk.clk
		input  wire       reset_reset_n,                            //                              reset.reset_n
		input  wire       rs232_0_avalon_data_receive_source_ready, // rs232_0_avalon_data_receive_source.ready
		output wire [7:0] rs232_0_avalon_data_receive_source_data,  //                                   .data
		output wire       rs232_0_avalon_data_receive_source_error, //                                   .error
		output wire       rs232_0_avalon_data_receive_source_valid, //                                   .valid
		input  wire [7:0] rs232_0_avalon_data_transmit_sink_data,   //  rs232_0_avalon_data_transmit_sink.data
		input  wire       rs232_0_avalon_data_transmit_sink_error,  //                                   .error
		input  wire       rs232_0_avalon_data_transmit_sink_valid,  //                                   .valid
		output wire       rs232_0_avalon_data_transmit_sink_ready,  //                                   .ready
		input  wire       rs232_0_external_interface_RXD,           //         rs232_0_external_interface.RXD
		output wire       rs232_0_external_interface_TXD,           //                                   .TXD
		input  wire       rs232_0_reset_reset                       //                      rs232_0_reset.reset
	);

	unsaved_rs232_0 rs232_0 (
		.clk             (clk_clk),                                  //                        clk.clk
		.reset           (rs232_0_reset_reset),                      //                      reset.reset
		.from_uart_ready (rs232_0_avalon_data_receive_source_ready), // avalon_data_receive_source.ready
		.from_uart_data  (rs232_0_avalon_data_receive_source_data),  //                           .data
		.from_uart_error (rs232_0_avalon_data_receive_source_error), //                           .error
		.from_uart_valid (rs232_0_avalon_data_receive_source_valid), //                           .valid
		.to_uart_data    (rs232_0_avalon_data_transmit_sink_data),   //  avalon_data_transmit_sink.data
		.to_uart_error   (rs232_0_avalon_data_transmit_sink_error),  //                           .error
		.to_uart_valid   (rs232_0_avalon_data_transmit_sink_valid),  //                           .valid
		.to_uart_ready   (rs232_0_avalon_data_transmit_sink_ready),  //                           .ready
		.UART_RXD        (rs232_0_external_interface_RXD),           //         external_interface.export
		.UART_TXD        (rs232_0_external_interface_TXD)            //                           .export
	);

endmodule
