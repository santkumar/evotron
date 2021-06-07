clear all;
close all;
clc;

%% Create directory for all experimental result-data
timeStamp = strrep(datestr(datetime), ':', '_');
resultDirectory = [pwd filesep timeStamp];
mkdir([resultDirectory]);

%% Log file
logFileID = fopen([resultDirectory filesep 'auto_sampler_log.txt'],'w');
fprintf(logFileID, [datestr(datetime) ' Auto-sampling for eVOLVER log file\r\n']);
fprintf(logFileID,'-------------------------------------------------------\r\n');

%% Commands 
% NOTE: Must end with ? and must contain only two alphabets
cmdStartSampling = "ss?";
cmdCytoAcquisitionStarted = "as?";
cmdCytoAcquisitionFinished = "af?";
cmdRemoveWaste = "rw?";
cmdCleanNeedle = "cn?";
cmdDone = "dn?";
cmdMoveNeedleForSampling = "mn?";
cmdError = "er?";

%% Open communication port with arduino
delete(instrfind());                            % delete all previous connections
arduinoComm = serialport('COM20',9600);         % check COM port with serialportlist("available") command
flush(arduinoComm);

%% Sampling loop
write(arduinoComm,cmdStartSampling,"string");   % send command to arduino to start sampling
fprintf(logFileID,[datestr(datetime) ' Sent command for sampling\r\n']);
while(~arduinoComm.NumBytesAvailable)           % wait until sampling is done
end
ack = read(arduinoComm,3,"string")             % length of cmdDone is 3

% test
% flush(arduinoComm);
while(~arduinoComm.NumBytesAvailable)           % wait until sampling is done
end
ack2 = read(arduinoComm,3,"string")             % length of cmdDone is 3


% if strcmp(ack,cmdDone)
%     fprintf(logFileID,[datestr(datetime) ' Sampling done\r\n']);
% else
%     fprintf(logFileID,[datestr(datetime) ' ERROR in start-sampling, Received ack from arduino: ' ack '\r\n']);
%     error('Error in start-sampling!');
% end
% flush(arduinoComm);
% ack = [];

%% Flow cytometer acquisition
% start cyto acquisition
% done cyto acquisition

%% Controller computations
% compute input light intensity
% send input light intensity to eVOLVER

%% Remove waste (dump sample from cyto)
fprintf(arduinoComm,cmdRemoveWaste);    % send command to arduino to start waste-removal
fprintf(logFileID,[datestr(datetime) ' Sent command for waste-removal\r\n']);
while(~arduinoComm.BytesAvailable)      % wait until waste-removal is done
end
fprintf(logFileID,[datestr(datetime) ' Waste-removal done\r\n']);
