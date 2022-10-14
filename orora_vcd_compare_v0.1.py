import sys

def main():
    args=sys.argv[1:]
    if(len(args)<2):
        print("################ Ororoa VCD Compare Tool #################")
        print("Written by Jiayi 10/14/2022")
        print("--usage:")
        print("# python orora_vcd_compare.py [input signal list] [vcdfile1] [vcdfile2] [starting timestamp]")
        return
    if(len(args)>=2):
        ts_bar=0
        if(len(args)==4):
            ts_bar=int(args[3])
        print("ts_bar=",ts_bar)
        signal_diff_ts={}
        signal_input=list()
        if(len(args)>=3):
            file_1=args[1]
            file_2=args[2]
            #parse input file
            with open(args[0]) as input_file:
                line = input_file.readline()
                while(line):
                    words=line.split()
                    if(len(words)>0):
                        if(words[0]=="input"):
                            signal_input.append(words[-1][:-1])
                    line = input_file.readline()
            print("There are", len(signal_input), "input signals.")
            print("input signals are: ")
            for signal in signal_input:
                print(signal)

        else:
            file_1=args[0]
            file_2=args[1]

        signal_map={}
        #read in signal definition
        with open(file_1) as file_signal:
            line = file_signal.readline()
            while(line):
                words=line.split()
                if(len(words)>0):
                    if(words[0]=="$var"):
                        if(words[3] in signal_map):
                            signal_map[words[3]].append(words[4])
                        else:
                            signal_map[words[3]]=[words[4]]
                    elif(words[0]=="$dumpvars"):
                        break
                line = file_signal.readline()
        """
        for signal in signal_map:
            if(signal=="Y("):
                print(signal,":",signal_map[signal])
        """

        for signal in signal_map:
            flag=1
            if(len(args)>=3):
                for signal_name in signal_map[signal]:
                    if(signal_name in signal_input):
                        flag=0
                if(flag):
                    #add this signal to dont-care
                    signal_diff_ts[signal]=0

        print("There are", len(signal_map), "signals in total.")
        print("Among them,", len(signal_map)-len(signal_diff_ts), "are input signals.")
        # Find and print the diff:
        current_timestamp=0
        signal_val_1={}
        signal_val_2={}

        ts_1=0
        ts_2=0

        #read in signals waveform
        with open(file_1) as file_1:
            with open(file_2) as file_2:
                file_1_line = file_1.readline()
                words1=file_1_line.split()
                #point to the beginning to timstamp
                while (len(words1)==0 or words1[0]!="$dumpvars"):
                    file_1_line = file_1.readline()
                    words1=file_1_line.split()

                file_2_line = file_2.readline()
                words2=file_2_line.split()
                while (len(words2)==0 or words2[0]!="$dumpvars"):
                    file_2_line = file_2.readline()
                    words2=file_2_line.split()

                #jump $dumpvars
                file_1_line = file_1.readline()
                file_2_line = file_2.readline()

                #print(file_1_line)
                #print(file_2_line)
                #initiate all signals in signal_map
                words1=file_1_line.split()
                while(words1[0][0]!='#' and words1[0]!="$end"):
                    if(len(words1)==1):
                        if(words1[0][1:] not in signal_diff_ts):
                            signal_val_1[words1[0][1:]]=words1[0][0]
                        #print(signal_map[words1[0][1:]],words1[0][0])
                    else:
                        if(words1[1] not in signal_diff_ts):
                            signal_val_1[words1[1]]=words1[0]
                        #print(signal_map[words1[1]],words1[0])
                    file_1_line = file_1.readline()
                    #print("file1_line_number=",file1_line_num)
                    if(file_1_line):
                        words1=file_1_line.split()
                    else: break

                #check file2 inital signal value
                words2=file_2_line.split()
                while(words2[0][0]!='#' and words2[0]!="$end"):
                    if(len(words2)==1):
                        if(words2[0][1:] not in signal_diff_ts):
                            if(signal_val_1[words2[0][1:]]!=words2[0][0]):
                                signal_val_2[words2[0][1:]]=words2[0][0]
                                signal_diff_ts[words2[0][1:]]=ts_2
                                print(signal_map[words2[0][1:]], "is different from two vcd files at timestamp [", ts_2, "]")
                            else:
                                signal_val_2[words2[0][1:]]=words2[0][0]
                    else:
                        if(words2[1] not in signal_diff_ts):
                            if(signal_val_1[words2[1]]!=words2[0]):
                                signal_val_2[words2[1]]=words2[0]
                                signal_diff_ts[words2[1]]=ts_2
                                print(signal_map[words2[1]], "is different from two vcd files at timestamp [", ts_2, "]")
                            else:
                                signal_val_2[words2[1]]=words2[0]
                    file_2_line = file_2.readline()
                    #print("file2_line_number=",file2_line_num)
                    if(file_2_line):
                        words2=file_2_line.split()
                    else: break
                
                #begin initial value parsing
                words1=file_1_line.split()
                words2=file_1_line.split()
                while(ts_1<ts_bar):
                    while(words1[0][0]!='#' and words1[0]!="$end"):
                        file_1_line = file_1.readline()
                        words1=file_1_line.split()
                    if(words1[0][0]=='#'):
                        ts_1=int(words1[0][1:])
                        #print("ts_1=",ts_1)
                    file_1_line = file_1.readline()
                    words1=file_1_line.split()

                while(ts_2<ts_bar or ts_2<ts_1):
                    while(words2[0][0]!='#' and words2[0]!="$end"):
                        file_2_line = file_2.readline()
                        words2=file_2_line.split()
                    if(words2[0][0]=='#'):
                        ts_2=int(words2[0][1:])
                        #print("ts_2=",ts_2)
                    file_2_line = file_2.readline()
                    words2=file_2_line.split()
                
                print("beginning timestamp at ts_1=", ts_1)

                words1=file_1_line.split()
                while(words1[0][0]!='#' and words1[0]!="$end"):
                    if(len(words1)==1):
                        if(words1[0][1:] not in signal_diff_ts):
                            signal_val_1[words1[0][1:]]=words1[0][0]
                        #print(signal_map[words1[0][1:]],words1[0][0])
                    else:
                        if(words1[1] not in signal_diff_ts):
                            signal_val_1[words1[1]]=words1[0]
                        #print(signal_map[words1[1]],words1[0])
                    file_1_line = file_1.readline()
                    #print("file1_line_number=",file1_line_num)
                    if(file_1_line):
                        words1=file_1_line.split()
                    else: break

                #check file2 inital signal value
                words2=file_2_line.split()
                while(words2[0][0]!='#' and words2[0]!="$end"):
                    if(len(words2)==1):
                        if(words2[0][1:] not in signal_diff_ts):
                            if(signal_val_1[words2[0][1:]]!=words2[0][0]):
                                signal_val_2[words2[0][1:]]=words2[0][0]
                                signal_diff_ts[words2[0][1:]]=ts_2
                                print(signal_map[words2[0][1:]], "is different from two vcd files at timestamp [", ts_2, "]")
                            else:
                                signal_val_2[words2[0][1:]]=words2[0][0]
                    else:
                        if(words2[1] not in signal_diff_ts):
                            if(signal_val_1[words2[1]]!=words2[0]):
                                signal_val_2[words2[1]]=words2[0]
                                signal_diff_ts[words2[1]]=ts_2
                                print(signal_map[words2[1]], "is different from two vcd files at timestamp [", ts_2, "]")
                            else:
                                signal_val_2[words2[1]]=words2[0]
                    file_2_line = file_2.readline()
                    #print("file2_line_number=",file2_line_num)
                    if(file_2_line):
                        words2=file_2_line.split()
                    else: break
                #skip $end
                file_1_line = file_1.readline()
                file_2_line = file_2.readline()

                #print("f1=", file_1_line)
                #print("f2=", file_2_line)

                #begin timestamp parsing
                print("")
                print("########## Begin Comparing ###########")
                print("")

                while(file_1_line or file_2_line):
                #some changes in file1 do not happen in file2
                    if(ts_1<ts_2):
                        words1=file_1_line.split()
                        #timestamp
                        if(words1[0][0]=='#'):
                            ts_1=int(words1[0][1:])
                            #print("ts_1=",ts_1)
                            file_1_line = file_1.readline()
                            words1=file_1_line.split()
                        #update value in signal_val
                        while(len(words1)>0 and words1[0][0]!='#' and words1[0]!="$end"):
                            #signal bit data
                            if(len(words1)==1):
                                #if haven't been excluded
                                if(words1[0][1:] not in signal_diff_ts):
                                    if(ts_1>ts_2):
                                        #check value at ts_2
                                        if(signal_val_1[words1[0][1:]] != signal_val_2[words1[0][1:]]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words1[0][1:]]=ts_2
                                                print(signal_map[words1[0][1:]], "is different from two vcd files at timestamp [", ts_2, "]")
                                        else:
                                            #record new value
                                            signal_val_1[words1[0][1:]]=words1[0][0]
                                            signal_val_2[words1[0][1:]]=words1[0][0]
                                    else:
                                        if(signal_val_1[words1[0][1:]] != words1[0][0]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words1[0][1:]]=ts_1
                                                print(signal_map[words1[0][1:]], "is different from two vcd files at timestamp [", ts_1, "]")
                                            

                            #multi-bit data
                            elif(len(words1)>0):
                                #if haven't been excluded
                                if(words1[1] not in signal_diff_ts):
                                    if(ts_1>ts_2):
                                        #check value at ts_2
                                        if(signal_val_1[words1[1]] != signal_val_2[words1[1]]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words1[1]]=ts_2
                                                print(signal_map[words1[1]], "is different from two vcd files at timestamp [", ts_2, "]")
                                        else:
                                            #record new value
                                            signal_val_1[words1[1]]=words1[0]
                                            signal_val_2[words1[1]]=words1[0]
                                    else:
                                        if(signal_val_1[words1[1]] != words1[0]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words1[1]]=ts_1
                                                print(signal_map[words1[1]], "is different from two vcd files at timestamp [", ts_1, "]")
                            #empty line
                            else: 
                                continue
                            file_1_line = file_1.readline()
                            #print("file1_line_number=",file1_line_num)
                            if(file_1_line):
                                words1=file_1_line.split()
                            else:break

                    #current timestamp is aligned, any change is valid
                    if(ts_1==ts_2):
                        words1=file_1_line.split()
                        #timestamp
                        if(words1[0][0]=='#'):
                            ts_1=int(words1[0][1:])
                            #print("ts_1=", ts_1)
                            file_1_line = file_1.readline()
                            words1=file_1_line.split()
                        #update value in signal_val
                        while(len(words1)>0 and words1[0][0]!='#' and words1[0]!="$end"):
                            #signal bit data
                            if(len(words1)==1):
                                if(words1[0][1:] not in signal_diff_ts):
                                    signal_val_1[words1[0][1:]]=words1[0][0]
                                #print(signal_map[words1[0][1:]],words1[0][0])
                            #multi-bit data
                            elif(len(words1)>0):
                                if(words1[1] not in signal_diff_ts):
                                    signal_val_1[words1[1]]=words1[0]
                                #print(signal_map[words1[1]],words1[0])
                            #empty line
                            else: 
                                continue
                            file_1_line = file_1.readline()
                            #print("file1_line_number=",file1_line_num)
                            if(file_1_line):
                                words1=file_1_line.split()
                            else:break

                    #check file2 tb
                    if(ts_2<ts_1):
                        words2=file_2_line.split()
                        #timestamp
                        if(words2[0][0]=='#'):
                            ts_2=int(words2[0][1:])
                            #print("ts_2=",ts_2)
                            file_2_line = file_2.readline()
                            words2=file_2_line.split()
                        #update value in signal_val
                        while(len(words2)>0 and words2[0][0]!='#' and words2[0]!="$end"):
                            #signal bit data
                            if(len(words2)==1):
                                #if haven't been excluded
                                if(words2[0][1:] not in signal_diff_ts):
                                    if(ts_2>ts_1):
                                        #check value at ts_1
                                        if(signal_val_2[words2[0][1:]] != signal_val_1[words2[0][1:]]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words2[0][1:]]=ts_1
                                                print(signal_map[words2[0][1:]], "is different from two vcd files at timestamp [", ts_1, "]")
                                                print("in vcd_file_1, it's ",signal_val_1[words2[0][1:]] )
                                                print("while in vcd_file_2, it's ",signal_val_2[words2[0][1:]] )
                                        else:
                                            #record new value
                                            signal_val_1[words2[0][1:]]=words2[0][0]
                                            signal_val_2[words2[0][1:]]=words2[0][0]
                                    else:
                                        if(signal_val_1[words2[0][1:]] != words2[0][0]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words2[0][1:]]=ts_2
                                                print(signal_map[words2[0][1:]], "is different from two vcd files at timestamp [", ts_2, "]")
                                                print("in vcd_file_1, it's ",signal_val_1[words2[0][1:]] )
                                                print("while in vcd_file_2, it's ",words2[0][0])

                            #multi-bit data
                            elif(len(words2)>0):
                                #if haven't been excluded
                                if(words2[1] not in signal_diff_ts):
                                    if(ts_2>ts_1):
                                        #check value at ts_1
                                        if(signal_val_2[words2[1]] != signal_val_1[words2[1]]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words2[1]]=ts_1
                                                print(signal_map[words2[1]], "is different from two vcd files at timestamp [", ts_1, "]")
                                                print("in vcd_file_1, it's ",signal_val_1[words2[1]] )
                                                print("while in vcd_file_2, it's ",signal_val_2[words2[1]] )
                                        else:
                                            #record new value
                                            signal_val_1[words2[1]]=words2[0]
                                            signal_val_2[words2[1]]=words2[0]
                                    else:
                                        if(signal_val_1[words2[1]] != words2[0]):
                                            if(ts_1>ts_bar and ts_2>ts_bar):
                                                signal_diff_ts[words2[1]]=ts_2
                                                print(signal_map[words2[1]], "is different from two vcd files at timestamp [", ts_2, "]")
                                                print("in vcd_file_1, it's ",signal_val_1[words2[1]] )
                                                print("while in vcd_file_2, it's ",words2[0] )
                            #empty line
                            else: 
                                continue
                            file_2_line = file_2.readline()
                            #print("file1_line_number=",file1_line_num)
                            if(file_2_line):
                                words2=file_2_line.split()
                            else:break

                    #print("current_line = ", file1_line_num, file2_line_num)    


if __name__ == "__main__":
    main()
