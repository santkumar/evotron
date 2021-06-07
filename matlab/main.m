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
% NOTE: Must end with ?
cmdStartSampling = 's?';
cmdCytoAcquisitionStarted = 'q?';
cmdCytoAcquisitionFinished = 'f?';
cmdRemoveWaste = 'r?';
cmdCleanNeedle = 'c?';
cmdDone = 'd?';

%% Open communication port with arduino
delete(instrfind());                % delete all previous connections
arduinoComm = serial('COM20');      % check COM port with serialportlist("available") command
fopen(arduinoComm);                 % open the port handle

%% Sampling loop
fprintf(arduinoComm,cmdStartSampling);  % send command to arduino to start sampling
fprintf(logFileID,[datestr(datetime) ' Sent command for sampling\r\n']);
while(~arduinoComm.BytesAvailable)      % wait until sampling is done
end
flushinput(arduinoComm);
fprintf(logFileID,[datestr(datetime) ' Sampling done\r\n']);

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
