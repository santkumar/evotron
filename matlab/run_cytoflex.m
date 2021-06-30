
executableFile = "C:\my_git_repo\evotron\cytoflex\routine\bin\Release\cyto_control.exe";
exptFile = "C:\my_git_repo\evotron\cytoflex\experiments\cyto_expt_file.xit";
desiredResultFormatFile = "C:\my_git_repo\evotron\cytoflex\experiments\xml_desired_result.xml";
outputResultFile = "C:\my_git_repo\evotron\cytoflex\experiments\acquisition_result.xml";
cytoRunCommand = join([executableFile, exptFile, desiredResultFormatFile, outputResultFile]);

count = 1;

% Run cytoflex acquisition
system(cytoRunCommand);

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

