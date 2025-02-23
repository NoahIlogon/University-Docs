import dask.dataframe as df

def main():
    # Bombing_Operations_df = df.read_parquet('/Users/noahilogon/Desktop/Uni/DATA301/Labs/Lab00/Bombing_Operations.parquet')
    # Bombing_Operations_df = Bombing_Operations_df.fillna('')
    # Bombing_Operations = Bombing_Operations_df.to_bag().persist()
    # column_indices = dict([(k, i) for i, k in enumerate(Bombing_Operations_df.columns)])
    # print(column_indices)

    # aircraft_counts = Bombing_Operations.foldby(
    # key=lambda x: x[2],         
    # binop=lambda x, y: x + 1,    
    # initial=0                    
    # )
    #
    # max(aircraft_counts, key=lambda x: x[1])[0]
    # 
    # most_used = max(map(lambda x: (x[0], x[1]), aircraft_counts), key=lambda x: x[1])[0]



    aircraft_counts = [('EC-47', 52865), ('RF-4', 242231), ('A-1', 358498), ('A-37', 267457), ('F-4', 909362), ('A-4', 372975), ('A-7', 165773), ('CH-53', 4339), ('O-1', 50843), ('UH-1', 146543), ('C-7', 13769), ('A-6', 144601), ('EB-66', 34738), ('T-28', 41655), ('C-123', 20604), ('CH-47', 9286),
            ('AC-47', 73843), ('AU-24', 5036), ('AC-130', 75058), ('F-105', 140410), ('AC-119', 76525), ('EC-121', 17226), ('B-52', 99100), ('C-119', 5085), ('B-57', 82219), ('F-111', 20441), ('C-130', 35333), ('QU-22', 4707), ('F-100', 451385), ('O-2', 30977), ('RF-101', 71716), ('U-6', 6218), ('UC-123', 2201), ('T-39', 106), ('F-5', 39999), ('OV-10', 24481), ('HH-53', 6903), ('C-47', 19721), ('HH-43', 10331), ('RC-135', 752), ('CH-46', 2571), ('E-1', 1498),
            ('EC-130', 5215), ('U-17', 26649), ('RC-47', 7800), ('KC-135', 8266), ('WC-130', 1223), ('KA-6', 385), ('HH-3', 875), ('HC-130', 6062), ('VC-47', 2290), ('CH-3', 1248), ('AH-1', 1292), ('U-21', 1838), ('RF-5', 1527), ('H-34', 2174), ('EKA-3', 2024), ('RB-57', 19443), ('KC-130', 1041), ('F-8', 58691), ('E-2', 1379), ('RA-5', 9947), ('DC-6', 342), ('RF-8', 10322), ('T-29', 456), ('C-1', 39), ('KA-7', 16), ('YQU-22', 1075), ('EA-6', 3905), ('KA3', 836),
            ('AC-123', 3434), ('F-102', 3882), ('VC-54', 43), ('U-3', 95), ('TA-4', 5954), ('EA-3', 6450), ('SH-3', 110), ('U-1', 176), ('NOT CODED', 1089), ('HC-47', 1076), ('DC-4', 55), ('T-41', 229), ('C-117', 982), ('EP-3', 203), ('H-47', 3), ('LC-130', 1), ('VC-118', 28), ('C-54', 13), ('A-3', 1213), ('A-26', 36242), ('TF9', 3600), ('B-66', 1052), ('EF-10', 7064), ('RB-66', 1968), ('F-104', 2913), ('EA-1', 4872), ('JC-47', 75), ('RA-3', 560), ('FC-47', 921),
            ('KA-4', 485), ('A-5', 8), ('NC-123', 7), ('A8', 4), ('F-9', 186), ('U-10', 5), ('T9', 4), ('R64', 1), ('OV-1', 10), ('R44', 1), ('EC-211', 2), ('UH-34', 2), ('F-10', 2), ('B-1', 2), ('F-14', 5), ('U-1A', 1), ('UC-130', 2), ('C-121', 1), ('P41', 1), ('E-3', 1), ('C-76', 1)]

    # most_used = max(aircraft_counts, key=lambda x: x[1])
    print(max(map(lambda x: (x[0], x[1]), aircraft_counts), key=lambda x: x[1])[0])


if __name__ == '__main__':
    main()
