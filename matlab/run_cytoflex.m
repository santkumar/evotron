temp = 1;

while 1
    
    check2 = dir('C:\my_git_repo\evotron\matlab\comm_folder_1');
    
    if length(check2)>2
        
        % Load count number variable: count
        load 'C:\my_git_repo\evotron\matlab\comm_folder_1\comm_check.mat';
        
        % Run cytoflex acquisition
        system("C:\my_git_repo\evotron\cytoflex\routine\bin\Release\cyto_control.exe");
        
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
        
        delete('C:\my_git_repo\evotron\matlab\comm_folder_1\*');
        save C:\my_git_repo\evotron\matlab\comm_folder_2\comm_check.mat temp
        
    end
    
end
