function main()

clear all;
close all;
clc;

% For stopping opentron routine with Ctrl+C key press
cleanupObj = onCleanup(@stop_routine);
opentronReturn = 1;

%% Run routine on Opentron
disp('May the force be with your experiment!')
disp('Connecting opentron...')
opentronReturn = system("C:\cygwin64\bin\sshpass -p 'openthetron' ssh -i ot2_dd037_ssh_key root@192.168.0.100 './run_opentron_script.sh'");
disp('Connection with opentron: Successful');
pause(30);

%%
executableFile = "C:\my_git_repo\evotron\cytoflex\routine\bin\Release\cyto_control.exe";
exptFile = "C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file.xit";
desiredResultFormatFile = "C:\my_git_repo\evotron\cytoflex\experiments\xml_desired_result.xml";
outputResultFile = "C:\my_git_repo\evotron\cytoflex\experiments\acquisition_result.xml";
cytoRunCommand = join([executableFile, exptFile, desiredResultFormatFile, outputResultFile]);

%% Create directory for all experimental result-data
timeStamp = strrep(datestr(datetime), ':', '_');
resultDirectory = [pwd filesep timeStamp];
mkdir([resultDirectory]);

%% Log file
logFileID = fopen([resultDirectory filesep 'auto_sampler_log.txt'],'w');
fprintf(logFileID, [datestr(datetime) ' Auto-sampling for eVOLVER log file\r\n']);
fprintf(logFileID,'-------------------------------------------------------\r\n');

%% Commands
% NOTE: Must end with ? and start with ! and must contain only three other alphabets
numCmdBytes = 5;
cmdStartSampling = "!ssa?";
cmdDoneSampling = "!dsa?";
cmdRemoveSampleAndClean = "!rsc?";
cmdDoneCleaning = "!dcl?";
cmdError = "!err?";
cmdStopProgram = "!stp?";

%% Open communication port with arduino
delete(instrfind());                            % delete all previous connections
arduinoComm = serialport('COM10',9600);         % check COM port with serialportlist("available") command
flush(arduinoComm);
disp('Connection with arduino: Successful');

count = 1;
%%
while 1
    tStart = tic;
    
    disp('----------------------------------------------------------------------')
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
    
    % if done sampling then start cytoflex acquisition
    disp('Starting cytoflex routine...');
    system(cytoRunCommand);     % run cytoflex acquisition
    
    % Copy and delete files for next acquisition
    delete('C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file.xit');
    copyfile('C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file\01-Well-A1.fcs', ...
        ['C:\my_git_repo\evotron\cytoflex\experiments\results\fcs_output\sample_' num2str(count) '.fcs']);
    delete('C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file\01-Well-A1.fcs');
    copyfile('C:\my_git_repo\evotron\cytoflex\experiments\sample_experiments\2021_06_23\cyto_expt_file.xit', ...
        'C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file.xit');
    copyfile('C:\my_git_repo\evotron\cytoflex\experiments\sample_experiments\2021_06_23\01-Well-A1.fcs', ...
        'C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file\01-Well-A1.fcs');
    copyfile('C:\my_git_repo\evotron\cytoflex\experiments\acquisition_result.xml', ...
        ['C:\my_git_repo\evotron\cytoflex\experiments\results\acquisition_result_' num2str(count) '.xml']);
    delete('C:\my_git_repo\evotron\cytoflex\experiments\acquisition_result.xml');
    
    fprintf(logFileID,[datestr(datetime) ' Cytoflex acquisition done\r\n']);
    
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
    
    tElapsed = toc(tStart);
    if tElapsed<1800
        pause(1800-tElapsed);
    end
    
end

    function stop_routine()
        
        disp('Ctrl + C detected, or main run ended gracefully!')
        fprintf(logFileID,[datestr(datetime) ' Ctrl + C detected, or main run ended gracefully. Stopping opentron routine!\r\n']);
        
        % Stop opentron routine
        disp('Stopping opentron and resetting arduino...');
        if (~opentronReturn) % execute only if opentron routine is running (return value is 0 for correct start) o/w do nothing
            system("C:\cygwin64\bin\sshpass -p 'openthetron' ssh -i ot2_dd037_ssh_key root@192.168.0.100 './stop_opentron_script.sh'");
            pause(1);
        end
        
        % Stop/reset arduino
        write(arduinoComm,cmdStopProgram,"string");     % send command to arduino to start sampling
        fprintf(logFileID,[datestr(datetime) ' Sent command for stopping/reset\r\n']);       
        while(~arduinoComm.NumBytesAvailable)           % wait until ack is received
        end
        ack = read(arduinoComm,numCmdBytes,"string");
        disp(ack);
        fprintf(logFileID,[datestr(datetime) ' Last received ack from arduino: %s \r\n'], ack);
        disp('See ya!');
        
        fclose(logFileID);
        
    end

end
