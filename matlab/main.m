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
% NOTE: Must end with ? and must contain only three other alphabets
numCmdBytes = 5;
cmdStartSampling = "!ssa?";
cmdDoneSampling = "!dsa?";
cmdRemoveSampleAndClean = "!rsc?";
cmdDoneCleaning = "!dcl?";
cmdError = "!err?";

%% Open communication port with arduino
delete(instrfind());                            % delete all previous connections
arduinoComm = serialport('COM19',9600);         % check COM port with serialportlist("available") command
flush(arduinoComm);

count = 1;
%%
while 1
tStart = tic;    

disp(['Started sampling #' num2str(count)]);

% Sampling loop
write(arduinoComm,cmdStartSampling,"string");   % send command to arduino to start sampling
fprintf(logFileID,[datestr(datetime) ' Sent command for sampling\r\n']);

while(~arduinoComm.NumBytesAvailable)           % wait until sampling is done
end
ack = read(arduinoComm,numCmdBytes,"string");             
disp(ack);
if strcmp(ack,cmdStartSampling)
    fprintf(logFileID,[datestr(datetime) ' Sampling command ack from arduino\r\n']);
else
    fprintf(logFileID,[datestr(datetime) ' ERROR in start-sampling, Received ack from arduino: %s \r\n'], ack);
    error('Error in start-sampling!');
end
flush(arduinoComm);
ack = [];

% while(~arduinoComm.NumBytesAvailable)           % wait until sampling is done
% end
% ack = read(arduinoComm,4,"string")              % length of cmdDoneSampling is 4
% flush(arduinoComm);
% ack = [];

while(~arduinoComm.NumBytesAvailable)           % wait until sampling is done
end
ack = read(arduinoComm,numCmdBytes,"string");
disp(ack);
if strcmp(ack,cmdDoneSampling)
    fprintf(logFileID,[datestr(datetime) ' Sampling done\r\n']);
else
    fprintf(logFileID,[datestr(datetime) ' ERROR in start-sampling, Received ack from arduino: %s \r\n'], ack);
    error('Error in start-sampling!');
end
flush(arduinoComm);
ack = [];

% % if done sampling then start cytoflex acquisition
% % start cyto acquisition
% save C:\my_git_repo\evotron\matlab\comm_folder_1\comm_check.mat count
% fprintf(logFileID,[datestr(datetime) ' Cytoflex acquisition started\r\n']);
% while 1
%     check1 = dir('C:\my_git_repo\evotron\matlab\comm_folder_2');
%     if length(check1)>2
%         break;
%     end
% end
% fprintf(logFileID,[datestr(datetime) ' Cytoflex acquisition done\r\n']);
% delete('C:\my_git_repo\evotron\matlab\comm_folder_2\*');
% 
% if done cytoflex acquisition then clean
write(arduinoComm,cmdRemoveSampleAndClean,"string");   % send command to arduino to start sampling
fprintf(logFileID,[datestr(datetime) ' Sent command for sample removal and cleaning\r\n']);
while(~arduinoComm.NumBytesAvailable)           % wait until sampling is done
end
ack = read(arduinoComm,numCmdBytes,"string");
disp(ack);
if strcmp(ack,cmdRemoveSampleAndClean)
    fprintf(logFileID,[datestr(datetime) ' Received sample removal and cleaning command ack from arduino\r\n']);
else
    fprintf(logFileID,[datestr(datetime) ' ERROR in sample removal and cleaning, Received ack from arduino: %s \r\n'], ack);
    error('Error in sample removal and cleaning!');
end
flush(arduinoComm);
ack = [];

%%%% FURTHER COMPUTATION %%%%

% extract data from cytoflex acquisition
% prepare for next acquisition

% Controller computations
% compute input light intensity
% send input light intensity to eVOLVER


% Wait for command from arduino that cleaning is done
while(~arduinoComm.NumBytesAvailable)          
end
ack = read(arduinoComm,numCmdBytes,"string");
disp(ack)
if strcmp(ack,cmdDoneCleaning)
    fprintf(logFileID,[datestr(datetime) ' Cleaning done\r\n']);
else
    fprintf(logFileID,[datestr(datetime) ' ERROR in cleaning, Received ack from arduino: %s \r\n'], ack);
    error('Error in cleaning!');
end
flush(arduinoComm);
ack = [];

display(['Done sampling #' num2str(count)]);
count = count + 1;

% tElapsed = toc(tStart);
% if tElapsed<1800
%     pause(1800-tElapsed);
% end

end