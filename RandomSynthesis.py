import os
import soundfile as sf
import random as rand
import numpy as np
import librosa
import glob
#import sys
#import json
#from pydub import AudioSegment

def main():
    
    DS_Path = "./DS/"              #방해소리경로
    HS_Path = "./HS/"              #사람소리경로
    DRS_Path = "./DronSound/"             #드론소리경로
    CS_Path = "./CombineSound"  #합친소리경로

    DisturbSound = []
    HumanSound = []
    DronSound = []
    
    for dir_path, dir_name, file_name in os.walk(DS_Path):    # 방해소리 종류(폴더명)
        DisturbSound.append(dir_name)
    
    for dir_path, dir_name, file_name in os.walk(HS_Path):    # 사람소리 종류(폴더명)
        HumanSound.append(dir_name)

    for dir_path, dir_name, file_name in os.walk(DRS_Path):   # 드론소리 종류(폴더명)
        DronSound.append(dir_name)
   
    Angles = ["_0","_20","_40","_60","_80","_100","_120","_140","_160","_180"] #소리의 각도(폴더명)

    Samplerate = 44100
    SNR_List = [1, 0.5, 0.25] #거리

    Random_seed = 3
    times = 0
    end_time = 10
    percent = 0.05

    rand.seed( Random_seed )

    if not os.path.exists(CS_Path):
        os.makedirs(CS_Path)

    while (True):

        if times >= end_time:
            print("Time = " + str(end_time) + "sec")
            break

        random_percent = rand.random()
        
        if random_percent >= percent:
            
            for Angle in Angles:
              
                for Gain in SNR_List:

                    # 사람소리, 드론소리 중에 한가지를 랜덤선택
                    random_HS = rand.sample(HumanSound[0],1)
                    random_DRS = rand.sample(DronSound[0],1)

                    # 사람소리의 각도중 랜덤선택
                    random_HSA = Angle
       
                    # 사람소리, 드론소리가 담긴 폴더의 wav파일중 한가지 선택
                    HS_file_list = os.listdir(HS_Path+random_HS[0]+"/"+random_HS[0]+str(random_HSA))
                    HS_file = [file for file in HS_file_list if file.endswith(".wav")]
                    
                    random_HSN = rand.sample(HS_file,1)

                    DRS_file_list = os.listdir(DRS_Path+random_DRS[0])
                    DRS_file = [file for file in DRS_file_list if file.endswith(".wav")]
                    random_DRSN = rand.sample(DRS_file,1)

                    #선택된 wav파일 load
                    x_target, x_target_samplerate = librosa.load(HS_Path+random_HS[0]+"/"+random_HS[0]+str(random_HSA)+"/"+random_HSN[0],sr = Samplerate, mono = False)

                    #사람소리 파일생성
                    x_target = x_target * Gain
                    x_target = x_target * 32768
                    x_target = np.array(x_target, dtype='int16')
                    x_target = x_target.T
                    sf.write(CS_Path+"/{}_{}{}_{}".format(Gain,random_HS[0],random_HSA,random_HSN[0]),x_target,Samplerate,"PCM_16")
            
                    #합친소리파일과 드론소리파일 load
                    x_dron, x_dron_samplerate = librosa.load(DRS_Path+random_DRS[0]+"/"+random_DRSN[0],sr = Samplerate, mono = False)
                    x_com, x_com_samplerate = librosa.load(CS_Path+"/{}_{}{}_{}".format(Gain,random_HS[0],random_HSA,random_HSN[0]), sr=Samplerate, mono = False)
            
                    #드론소리의 랜덤부분과 합친소리를 합치고 파일생성
                    randomslice = rand.randrange(0,len(x_dron[0,:])-len(x_com[0,:]))
                    x_dron = x_dron[:,randomslice:randomslice+len(x_com[0,:])]
                    # sf.write((CS_Path+"/{}_{}.wav".format(random_DRS[0],random_DRSN)),x_dron,Samplerate,"PCM_16")

                    # x_dron, x_dron_samplerate = librosa.load(CS_Path+"/{}_{}.wav".format(random_DRS[0],random_DRSN),sr = Samplerate, mono = False)

                    x_mix_Dron = x_com + Gain * x_dron
                    x_mix_Dron = x_mix_Dron * 32768
                    x_mix_Dron = np.array(x_mix_Dron, dtype='int16')
                    x_mix_Dron = x_mix_Dron.T
                    
                    sf.write((CS_Path+"/{}_Com_{}_{}{}_{}".format(Gain,random_HS[0],random_DRS[0],random_HSA,random_HSN[0])),x_mix_Dron,Samplerate,"PCM_16")
                    
                    time = np.arange(len(x_mix_Dron))/float(Samplerate)
                    times += time[-1]

        else:

            for Angle in Angles:
            
                for Gain in SNR_List: 
        
                    #방해소리, 사람소리, 드론소리 중에 한가지를 랜덤선택
                    random_DS = rand.sample(DisturbSound[0],1)
                    random_HS = rand.sample(HumanSound[0],1)
                    random_DRS = rand.sample(DronSound[0],1)

                    #방해소리, 사람소리의 각도중 랜덤선택        
                    random_DSA = Angle
                    random_HSA = Angle
        
                    #방해소리, 사람소리, 드론소리가 담긴 폴더의 wav파일중 한가지 선택
                    DS_file_list = os.listdir(DS_Path+random_DS[0]+"/"+random_DS[0]+str(random_DSA))
                    DS_file = [file for file in DS_file_list if file.endswith(".wav")]
                        
                    random_DSN = rand.sample(DS_file,1)

                    HS_file_list = os.listdir(HS_Path+random_HS[0]+"/"+random_HS[0]+str(random_HSA))
                    HS_file = [file for file in HS_file_list if file.endswith(".wav")]
                        
                    random_HSN = rand.sample(HS_file,1)

                    DRS_file_list = os.listdir(DRS_Path+random_DRS[0])
                    DRS_file = [file for file in DRS_file_list if file.endswith(".wav")]
                    random_DRSN = rand.sample(DRS_file,1)

                    #선택된 wav파일 load
                    x_interf, x_interf_samplerate = librosa.load(DS_Path+random_DS[0]+"/"+random_DS[0]+str(random_DSA)+"/"+random_DSN[0],sr = Samplerate, mono = False)
                    x_target, x_target_samplerate = librosa.load(HS_Path+random_HS[0]+"/"+random_HS[0]+str(random_HSA)+"/"+random_HSN[0],sr = Samplerate, mono = False)


                    #방해소리와 사람소리를 합치고 파일생성
                    if len(x_interf[0,:]) >= len(x_target[0,:]):
                        x_long = x_interf
                        x_short = x_target
                        gain_long = random_percent
                        gain_short =Gain
                    else:
                        x_long = x_target
                        x_short = x_interf
                        gain_long = Gain
                        gain_short = random_percent
                    
                    x_zeros = np.zeros((len(x_short[:,0]), len(x_short[0,:])))
                    x_concat = np.concatenate((x_zeros,x_long,x_zeros),axis=1)
                    rp = rand.randrange(len(x_short[0,:]),len(x_concat[0,:])-len(x_short[0,:]))
                    
                    x_mix =  gain_long * x_concat[:,rp:rp+len(x_short[0,:])] + gain_short * x_short
                    if np.max(np.abs(x_mix)) > 1.0:
                        x_mix = x_mix / np.max(np.abs(x_mix))

                    x_mix = x_mix * 32768
                    x_mix = np.array(x_mix, dtype='int16')
                    x_mix = x_mix.T
                    sf.write((CS_Path+"/{}_{}{}_{}_{}{}_{}".format(Gain,random_HS[0],random_HSA,random_HSN[0].split(".")[0],random_DS[0],random_DSA,random_DSN[0])),x_mix,Samplerate,"PCM_16")
                    
            
                    #합친소리파일과 드론소리파일 load
                    x_dron, x_dron_samplerate = librosa.load(DRS_Path+random_DRS[0]+"/"+str(random_DRSN)+".wav",sr = Samplerate, mono=False)
                    x_com, x_com_samplerate = librosa.load(CS_Path+"/{}_{}{}_{}_{}{}_{}".format(Gain,random_HS[0],random_HSA,random_HSN[0].split(".")[0],random_DS[0],random_DSA,random_DSN[0]), sr=Samplerate, mono=False)
            
                    #드론소리의 랜덤부분과 합친소리를 합치고 파일생성 
                    # print(len(x_dron) - len(x_com))
                    # import pdb; pdb.set_trace()
                    randomslice2 = rand.randrange(0,len(x_dron[0,:])-len(x_com[0,:]))
                    x_dron = x_dron[:,randomslice2:randomslice2+len(x_com[0,:])]
            
                    x_mix_Dron = x_com + Gain * x_dron
                    x_mix_Dron = x_mix_Dron * 32768
                    x_mix_Dron = np.array(x_mix_Dron, dtype='int16')
                    x_mix_Dron = x_mix_Dron.T
                    
                    sf.write((CS_Path+"/{}_Com_{}{}_{}_{}{}_{}_{}.wav".format(Gain,random_DRS[0],random_HS[0],random_HSA,random_HSN[0].split(".")[0],random_DS[0],random_DSA,random_DSN[0])),x_mix_Dron,Samplerate,"PCM_16")

                    time = np.arange(len(x_mix_Dron))/float(Samplerate)
                    times += time[-1]
        
if __name__ == '__main__':
    main()