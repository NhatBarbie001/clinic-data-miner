# Báo cáo cấu trúc P2: cây chương → bệnh → mục

## 1. Tổng quan

- Lần chạy `p2_tree_20261023-170706-193_ebb2` · **success** · 2.991s · git `c240d8d` · LLM: 0 lời gọi, $0.000000 · prompt dùng: không
- Cây: **35 chương · 334 bệnh · 2461 mục · 2 mục con** · có phần đầu · 6642 block
- Cấp tiêu đề: quy tắc 2801 · xác nhận/sửa bằng mục lục 42 · LLM 0
- Loại mục: từ điển 2461 · khớp gần 0 · kế thừa 2 · LLM 0 · chưa rõ 0

| Bệnh | Trang PDF | Trang in | Mục / mục con | Block | Số từ |
|---|---|---|---|---|---|
| Peripheral Neuropathy | 55–55 | 39–39 | 14 | 38 | 360 |
| Stump Pain | 55–56 | 39–40 | 14 | 32 | 176 |
| Phantom Pain | 56–56 | 40–40 | 12 | 29 | 225 |
| Complex Regional Pain Syndromes (CRPS) | 56–57 | 40–41 | 0 | 9 | 325 |
| Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) | 57–58 | 41–42 | 14 | 35 | 512 |
| Complex Regional Pain Syndrome, Type II (Causalgia) | 58–59 | 42–43 | 13 | 33 | 443 |
| Central Pain | 59–60 | 43–44 | 13 | 35 | 641 |
| Syndrome of Syringomyelia | 60–60 | 44–44 | 12 | 28 | 411 |
| Polymyalgia Rheumatica | 60–61 | 44–45 | 15 | 39 | 262 |
| Fibromyalgia (or Fibrositis) | 61–63 | 45–47 | 17 | 42 | 1072 |
| Note: Specific Myofascial Pain Syndromes | 63–63 | 47–47 | 0 | 4 | 175 |
| Rheumatoid Arthritis | 63–64 | 47–48 | 14 | 42 | 519 |
| Osteoarthritis | 64–65 | 48–49 | 15 | 32 | 452 |
| Calcium Pyrophosphate Dihydrate Deposition Disease (CPPD) | 65–65 | 49–49 | 13 | 30 | 318 |
| Gout | 65–66 | 49–50 | 15 | 35 | 370 |
| Hemophilic Arthropathy | 66–68 | 50–52 | 17 | 43 | 1190 |
| Burns | 68–69 | 52–53 | 12 | 27 | 597 |
| Pain of Psychological Origin: Muscle Tension Pain | 69–69 | 53–53 | 12 | 26 | 319 |
| Pain of Psychological Origin: Delusional or Hallucinatory | 69–70 | 53–54 | 10 | 27 | 280 |
| Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal | 70–72 | 54–56 | 12 | 33 | 1083 |
| Pain of Psychological Origin: Associated with Depression | 72–72 | 56–56 | 11 | 25 | 468 |
| A Note on Factitious Illness and Malingering | 72–73 | 56–57 | 0 | 2 | 132 |
| Regional Sprains or Strains | 73–73 | 57–57 | 1 | 3 | 1 |
| Sickle Cell Arthropathy | 73–73 | 57–57 | 1 | 3 | 1 |
| Purpuric Arthropathy | 73–73 | 57–57 | 1 | 3 | 1 |
| Stiff Man Syndrome | 73–73 | 57–57 | 1 | 3 | 1 |
| Paralysis Agitans | 73–73 | 57–57 | 1 | 3 | 1 |
| Epilepsy | 73–73 | 57–57 | 1 | 3 | 1 |
| Polyarteritis Nodosa | 73–73 | 57–57 | 1 | 3 | 1 |
| Psoriatic Arthropathy and Other Secondary Arthropathies | 73–73 | 57–57 | 1 | 3 | 1 |
| Painful Scar | 73–73 | 57–57 | 1 | 3 | 3 |
| Systemic Lupus Erythematosis, Systemic Sclerosis and Fibrosclerosis, Polymyositis, and Dermatomyositis | 73–73 | 57–57 | 1 | 3 | 1 |
| Infective Arthropathies | 73–73 | 57–57 | 1 | 3 | 1 |
| Traumatic Arthropathy | 73–73 | 57–57 | 1 | 3 | 1 |
| Osteomyelitis | 73–73 | 57–57 | 1 | 3 | 1 |
| Osteitis Deformans | 73–73 | 57–57 | 1 | 3 | 1 |
| Osteochondritis | 73–73 | 57–57 | 1 | 3 | 1 |
| Osteoporosis | 73–73 | 57–57 | 1 | 3 | 1 |
| Muscle Spasm | 74–74 | 58–58 | 1 | 3 | 1 |
| Local Pain, No Cause Specified | 74–74 | 58–58 | 1 | 3 | 3 |
| Guillain-Barre Syndrome | 74–74 | 58–58 | 12 | 25 | 286 |
| Trigeminal Neuralgia (Tic Douloureux) | 75–76 | 59–60 | 15 | 33 | 620 |
| Secondary Neuralgia (Trigeminal) from Central Nervous System Lesions | 76–76 | 60–60 | 14 | 32 | 265 |
| Secondary Trigeminal Neuralgia from Facial Trauma | 76–77 | 60–61 | 10 | 21 | 110 |
| Acute Herpes Zoster (Trigeminal) | 77–77 | 61–61 | 13 | 26 | 223 |
| Postherpetic Neuralgia (Trigeminal) | 77–78 | 61–62 | 13 | 26 | 220 |
| Geniculate Neuralgia (VIIth Cranial Nerve): Ramsay Hunt Syndrome | 78–78 | 62–62 | 11 | 22 | 117 |
| Neuralgia of the Nervus Intermedius | 78–79 | 62–63 | 15 | 33 | 278 |
| Glossopharyngeal Neuralgia (IXth Cranial Nerve) | 79–79 | 63–63 | 13 | 27 | 252 |
| Neuralgia of the Superior Laryngeal Nerve (Vagus Nerve Neuralgia) | 80–80 | 64–64 | 14 | 29 | 212 |
| Occipital Neuralgia | 80–81 | 64–65 | 14 | 33 | 268 |
| Hypoglossal Neuralgia | 81–81 | 65–65 | 1 | 3 | 1 |
| Glossopharyngeal Pain from Trauma | 81–81 | 65–65 | 1 | 3 | 1 |
| Hypoglossal Pain from Trauma | 81–81 | 65–65 | 1 | 3 | 1 |
| Tolosa-Hunt Syndrome (Painful Ophthalmoplegia) | 81–82 | 65–66 | 15 | 34 | 423 |
| SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing) | 82–83 | 66–67 | 14 | 32 | 503 |
| Raeder’s Syndrome (Raeder’s Paratrigeminal Syndrome) | 83–84 | 67–68 | 15 | 36 | 735 |
| Acute Tension Headache | 84–84 | 68–68 | 5 | 12 | 169 |
| Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) | 84–85 | 68–69 | 16 | 38 | 816 |
| Temporomandibular Pain and Dysfunction Syndrome | 86–86 | 70–70 | 14 | 40 | 599 |
| Osteoarthritis of the Temporomandibular Joint | 87–87 | 71–71 | 1 | 3 | 1 |
| Rheumatoid Arthritis of the Temporomandibular Joint | 87–87 | 71–71 | 14 | 29 | 175 |
| Dystonic Disorders, Facial Dyskinesia | 87–87 | 71–71 | 1 | 3 | 1 |
| Crushing Injury of Head or Face | 87–87 | 71–71 | 1 | 3 | 1 |
| Maxillary Sinusitis | 88–88 | 72–72 | 12 | 25 | 283 |
| Odontalgia: Toothache 1. Due to Dentino-Enamel Defects | 88–89 | 72–73 | 13 | 27 | 132 |
| Odontalgia: Toothache 2. Pulpitis | 89–89 | 73–73 | 13 | 27 | 225 |
| Odontalgia: Toothache 3. Periapical Periodontitis and Abscess | 89–90 | 73–74 | 14 | 31 | 200 |
| Odontalgia: Toothache 4. Tooth Pain Not Associated with Lesions (Atypical Odontalgia) | 90–90 | 74–74 | 12 | 27 | 227 |
| Glossodynia and Sore Mouth | 90–91 | 74–75 | 12 | 31 | 430 |
| Cracked Tooth Syndrome | 91–92 | 75–76 | 13 | 27 | 184 |
| Dry Socket | 92–92 | 76–76 | 12 | 28 | 280 |
| Gingival Disease, Inflammatory | 92–92 | 76–76 | 1 | 3 | 1 |
| Toothache, Cause Unknown | 92–92 | 76–76 | 1 | 3 | 1 |
| Diseases of the Jaw, Inflammatory Conditions | 92–92 | 76–76 | 1 | 3 | 1 |
| Other and Unspecified Pain in Jaws | 92–92 | 76–76 | 1 | 3 | 1 |
| Frostbite of Face | 92–92 | 76–76 | 1 | 3 | 2 |
| Classic Migraine (Migraine with Aura) | 93–94 | 77–78 | 16 | 37 | 716 |
| Common Migraine (Migraine without Aura) | 94–94 | 78–78 | 9 | 26 | 332 |
| Migraine Variants | 94–95 | 78–79 | 2 | 12 | 137 |
| Carotidynia | 95–95 | 79–79 | 10 | 24 | 361 |
| Mixed Headache | 95–95 | 79–79 | 1 | 4 | 37 |
| Cluster Headache | 95–96 | 79–80 | 15 | 36 | 654 |
| Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety) | 97–98 | 81–82 | 16 | 36 | 680 |
| Chronic Paroxysmal Hemicrania (CPH) (Remitting Form or Variety) | 98–98 | 82–82 | 7 | 18 | 242 |
| Chronic Cluster Headache | 98–99 | 82–83 | 7 | 19 | 259 |
| Cluster-Tic Syndrome | 99–99 | 83–83 | 16 | 34 | 461 |
| Post-traumatic Headache | 100–100 | 84–84 | 13 | 30 | 395 |
| The Syndrome of “Jabs and Jolts” | 100–101 | 84–85 | 14 | 34 | 614 |
| Temporal Arteritis (Giant Cell Arteritis) | 101–102 | 85–86 | 16 | 44 | 567 |
| Headache Associated with Low CSF Pressure | 102–103 | 86–87 | 15 | 34 | 367 |
| Post-Dural Puncture Headache | 103–104 | 87–88 | 15 | 32 | 333 |
| Hemicrania Continua | 104–105 | 88–89 | 15 | 33 | 495 |
| Headache Not Otherwise Specified | 105–105 | 89–89 | 0 | 2 | 2 |
| Delusional or Hallucinatory Pain | 109–109 | 93–93 | 1 | 6 | 13 |
| Hysterical, Conversion, or Hypochondriacal Pain | 109–109 | 93–93 | 1 | 7 | 39 |
| Associated with Depression | 109–109 | 93–93 | 1 | 5 | 6 |
| Stylohyoid Process Syndrome (Eagle’s Syndrome) | 109–110 | 93–94 | 14 | 29 | 155 |
| Cervicogenic Headache | 110–111 | 94–95 | 17 | 39 | 774 |
| Superior Pulmonary Sulcus Syndrome (Pancoast Tumor) | 111–112 | 95–96 | 13 | 29 | 389 |
| Thoracic Outlet Syndrome | 112–113 | 96–97 | 13 | 32 | 686 |
| Cervical Rib or Malformed First Thoracic Rib | 113–113 | 97–97 | 0 | 2 | 65 |
| Pain of Skeletal Metastatic Disease of the Neck, Arm, or Shoulder Girdle | 113–113 | 97–97 | 11 | 23 | 284 |
| Carcinoma of Thyroid | 114–114 | 98–98 | 9 | 19 | 63 |
| Carcinoma of Larynx | 114–114 | 98–98 | 10 | 22 | 118 |
| Tuberculosis of Larynx | 114–115 | 98–99 | 11 | 22 | 120 |
| Chronic Pharyngitis | 115–115 | 99–99 | 1 | 5 | 5 |
| Carcinoma of Pharynx | 115–115 | 99–99 | 1 | 3 | 1 |
| Cervical Spinal or Radicular Pain Attributable to a Fracture | 119–119 | 103–103 | 4 | 29 | 175 |
| Cervical Spinal or Radicular Pain Attributable to an Infection | 119–120 | 103–104 | 4 | 33 | 233 |
| Cervical Spinal or Radicular Pain Attributable to a Neoplasm | 120–120 | 104–104 | 4 | 33 | 219 |
| Cervical Spinal or Radicular Pain Attributable to Metabolic Bone Disease | 120–121 | 104–105 | 4 | 20 | 110 |
| Cervical Spinal or Radicular Pain Attributable to Arthritis | 121–121 | 105–105 | 6 | 22 | 229 |
| Cervical Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | 121–122 | 105–106 | 5 | 11 | 106 |
| Cervical Spinal Pain of Unknown or Uncertain Origin | 122–122 | 106–106 | 5 | 12 | 178 |
| Upper Cervical Spinal Pain of Unknown or Uncertain Origin | 122–122 | 106–106 | 5 | 12 | 42 |
| Lower Cervical Spinal Pain of Unknown or Uncertain Origin | 122–122 | 106–106 | 6 | 13 | 41 |
| Cervico-Thoracic Spinal Pain of Unknown or Uncertain Origin | 122–123 | 106–107 | 4 | 10 | 38 |
| Acceleration-Deceleration Injury of the Neck (Cervical Sprain) | 123–123 | 107–107 | 7 | 20 | 350 |
| Torticollis (Spasmodic Torticollis) | 123–124 | 107–108 | 6 | 22 | 284 |
| Cervical Discogenic Pain | 124–124 | 108–108 | 7 | 31 | 438 |
| Cervical Zygapophysial Joint Pain | 124–125 | 108–109 | 7 | 39 | 604 |
| Cervical Muscle Sprain | 125–126 | 109–110 | 6 | 17 | 166 |
| Cervical Trigger Point Syndrome | 126–127 | 110–111 | 7 | 40 | 391 |
| Alar Ligament Sprain | 127–127 | 111–111 | 6 | 13 | 154 |
| Cervical Segmental Dysfunction | 127–127 | 111–111 | 6 | 17 | 232 |
| Radicular Pain Attributable to a Prolapsed Cervical Disk | 127–127 | 111–111 | 1 | 4 | 2 |
| Traumatic Avulsion of Nerve Roots | 127–127 | 111–111 | 1 | 3 | 3 |
| Thoracic Spinal or Radicular Pain Attributable to a Fracture | 128–128 | 112–112 | 4 | 23 | 123 |
| Thoracic Spinal or Radicular Pain Attributable to an Infection | 128–128 | 112–112 | 4 | 31 | 213 |
| Thoracic Spinal or Radicular Pain Attributable to a Neoplasm | 129–129 | 113–113 | 4 | 35 | 217 |
| Thoracic Spinal or Radicular Pain Attributable to Metabolic Bone Disease | 129–129 | 113–113 | 4 | 21 | 108 |
| Thoracic Spinal or Radicular Pain Attributable to Arthritis | 130–130 | 114–114 | 5 | 22 | 154 |
| Thoracic Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | 130–130 | 114–114 | 5 | 11 | 102 |
| Pain Referred from Thoracic Viscera or Vessels and Perceived as Thoracic Spinal Pain | 130–130 | 114–114 | 4 | 14 | 90 |
| Thoracic Spinal Pain of Unknown or Uncertain Origin | 130–131 | 114–115 | 5 | 12 | 183 |
| Upper Thoracic Spinal Pain of Unknown or Uncertain Origin | 131–131 | 115–115 | 6 | 13 | 43 |
| Midthoracic Spinal Pain of Unknown or Uncertain Origin | 131–131 | 115–115 | 5 | 12 | 42 |
| Lower Thoracic Spinal Pain of Unknown or Uncertain Origin | 131–131 | 115–115 | 6 | 13 | 43 |
| Thoracolumbar Spinal Pain of Unknown or Uncertain Origin | 131–132 | 115–116 | 6 | 13 | 40 |
| Thoracic Discogenic Pain | 132–132 | 116–116 | 6 | 28 | 371 |
| Thoracic Zygapophysial Joint Pain | 132–133 | 116–117 | 7 | 31 | 323 |
| Costo-Transverse Joint Pain | 133–133 | 117–117 | 5 | 27 | 346 |
| Thoracic Muscle Sprain | 133–134 | 117–118 | 5 | 17 | 140 |
| Thoracic Trigger Point Syndrome | 134–134 | 118–118 | 7 | 24 | 267 |
| Thoracic Muscle Spasm | 134–135 | 118–119 | 7 | 24 | 248 |
| Thoracic Segmental Dysfunction | 135–135 | 119–119 | 6 | 19 | 241 |
| Radicular Pain Attributable to a Prolapsed Thoracic Disk | 135–135 | 119–119 | 1 | 6 | 9 |
| Tumors of the Brachial Plexus | 137–137 | 121–121 | 13 | 30 | 376 |
| Chemical Irritation of the Brachial Plexus | 137–138 | 121–122 | 12 | 27 | 261 |
| Traumatic Avulsion of the Brachial Plexus | 138–139 | 122–123 | 13 | 29 | 919 |
| Postradiation Pain of the Brachial Plexus | 139–139 | 123–123 | 1 | 3 | 1 |
| Painful Arms and Moving Fingers | 139–139 | 123–123 | 2 | 6 | 25 |
| Brachial Neuritis (Brachial Neuropathy, Neuralgic Amyotrophy, Parsonage-Turner Syndrome) | 139–140 | 123–124 | 9 | 19 | 143 |
| Bicipital Tendinitis | 140–140 | 124–124 | 13 | 27 | 128 |
| Subacromial Bursitis (Subdeltoid Bursitis, Supraspinatus Tendinitis) | 140–141 | 124–125 | 13 | 27 | 157 |
| Rotator Cuff Tear—Partial or Complete | 141–141 | 125–125 | 10 | 21 | 117 |
| Adhesive Capsulitis and Frozen Shoulder | 141–141 | 125–125 | 1 | 6 | 6 |
| Lateral Epicondylitis (Tennis Elbow) | 141–142 | 125–126 | 12 | 25 | 127 |
| Medial Epicondylitis (Golfer’s Elbow) | 142–142 | 126–126 | 9 | 19 | 45 |
| DeQuervain’s Tenosynovitis | 142–142 | 126–126 | 12 | 25 | 133 |
| Osteoarthritis of the Hands | 142–143 | 126–127 | 7 | 15 | 126 |
| Cubital Tunnel Syndrome | 143–143 | 127–127 | 9 | 20 | 212 |
| Carpal Tunnel Syndrome | 143–144 | 127–128 | 11 | 23 | 217 |
| Pain of Psychological Origin in the Shoulder and Arm | 144–144 | 128–128 | 1 | 7 | 13 |
| Crush Injury of Upper Limbs | 144–144 | 128–128 | 1 | 3 | 1 |
| Pain in a Limb or Limbs, Not Otherwise Specified | 144–144 | 128–128 | 1 | 5 | 10 |
| Raynaud’s Disease | 144–145 | 128–129 | 10 | 39 | 505 |
| Raynaud’s Phenomenon | 145–145 | 129–129 | 4 | 12 | 60 |
| Frostbite and Cold Injury | 145–146 | 129–130 | 12 | 28 | 468 |
| Erythema Pernio (Chilblains) | 146–146 | 130–130 | 6 | 16 | 138 |
| Acrocyanosis | 146–146 | 130–130 | 7 | 17 | 76 |
| Livedo Reticularis | 146–147 | 130–131 | 5 | 11 | 76 |
| Volkmann’s Ischemic Contracture | 147–147 | 131–131 | 1 | 2 | 0 |
| Scleroderma | 147–147 | 131–131 | 6 | 15 | 200 |
| Ergotism | 147–148 | 131–132 | 11 | 30 | 360 |
| Erythromelalgia | 148–148 | 132–132 | 10 | 28 | 260 |
| Thromboangiitis Obliterans | 149–149 | 133–133 | 14 | 33 | 470 |
| Chronic Venous Insufficiency | 149–150 | 133–134 | 14 | 36 | 359 |
| Intermittent Claudication (XV-1) and Rest Pain | 150–151 | 134–135 | 16 | 42 | 539 |
| Gangrene Due to Arterial Insufficiency | 151–151 | 135–135 | 1 | 5 | 4 |
| Acute Herpes Zoster | 153–153 | 137–137 | 1 | 3 | 1 |
| Postherpetic Neuralgia | 153–153 | 137–137 | 1 | 4 | 36 |
| Postinfectious and Segmental Peripheral Neuralgia | 153–153 | 137–137 | 7 | 18 | 178 |
| Angina Pectoris | 153–154 | 137–138 | 12 | 26 | 402 |
| Myocardial Infarction | 154–155 | 138–139 | 13 | 29 | 341 |
| Pericarditis | 155–155 | 139–139 | 13 | 33 | 288 |
| Aneurysm of the Aorta | 155–156 | 139–140 | 14 | 31 | 272 |
| Diseases of the Diaphragm | 156–157 | 140–141 | 13 | 33 | 388 |
| Carcinoma of Esophagus | 157–157 | 141–141 | 13 | 27 | 239 |
| Slipping Rib Syndrome | 157–158 | 141–142 | 15 | 32 | 318 |
| Postmastectomy Pain Syndrome: Chronic Nonmalignant | 158–158 | 142–142 | 13 | 29 | 189 |
| Late Postmastectomy Pain or Regional Carcinoma | 159–159 | 143–143 | 12 | 26 | 309 |
| Post-thoracotomy Pain Syndrome | 159–160 | 143–144 | 12 | 27 | 358 |
| Internal Mammary Artery Syndrome | 160–161 | 144–145 | 15 | 31 | 393 |
| Tietze’s Syndrome— Costo-Chondritis | 161–161 | 145–145 | 1 | 3 | 1 |
| Fractured Ribs or Sternum | 161–161 | 145–145 | 1 | 3 | 1 |
| Xiphoidalgia Syndrome | 161–161 | 145–145 | 2 | 5 | 16 |
| Carcinoma of the Lung or Pleura | 161–161 | 145–145 | 1 | 3 | 1 |
| Muscle Tension Pain | 161–161 | 145–145 | 5 | 11 | 98 |
| Delusional Pain | 161–161 | 145–145 | 1 | 4 | 16 |
| Conversion Pain | 161–161 | 145–145 | 2 | 6 | 48 |
| With Depression | 161–161 | 145–145 | 1 | 4 | 6 |
| Subphrenic Abscess | 162–162 | 146–146 | 13 | 29 | 218 |
| Herniated Abdominal Organs | 162–163 | 146–147 | 13 | 29 | 228 |
| Esophageal Motility Disorders | 163–164 | 147–148 | 13 | 28 | 533 |
| Esophagitis | 164–164 | 148–148 | 11 | 25 | 158 |
| Reflux Esophagitis with Peptic Ulceration | 164–165 | 148–149 | 13 | 27 | 322 |
| Gastric Ulcer with Chest Pain | 165–165 | 149–149 | 1 | 3 | 1 |
| Duodenal Ulcer with Chest Pain | 165–165 | 149–149 | 1 | 3 | 1 |
| Thoracic Visceral Disease with Pain Referred to Abdomen | 165–165 | 149–149 | 0 | 2 | 7 |
| Acute Herpes Zoster | 165–165 | 149–149 | 1 | 3 | 1 |
| Postherpetic Neuralgia | 165–165 | 149–149 | 1 | 3 | 1 |
| Segmental or Intercostal Neuralgia | 165–165 | 149–149 | 2 | 8 | 42 |
| Twelfth Rib Syndrome | 165–166 | 149–150 | 17 | 35 | 359 |
| Abdominal Cutaneous Nerve Entrapment Syndrome | 166–166 | 150–150 | 7 | 17 | 281 |
| Cardiac Failure | 167–167 | 151–151 | 13 | 27 | 209 |
| Gallbladder Disease | 167–168 | 151–152 | 12 | 25 | 187 |
| Post-cholecystectomy Syndrome | 168–168 | 152–152 | 12 | 25 | 144 |
| Chronic Gastric Ulcer | 168–169 | 152–153 | 12 | 25 | 339 |
| Chronic Duodenal Ulcer | 169–169 | 153–153 | 12 | 25 | 267 |
| Carcinoma of the Stomach | 169–170 | 153–154 | 12 | 26 | 367 |
| Carcinoma of the Pancreas | 170–170 | 154–154 | 12 | 27 | 326 |
| Chronic Mesenteric Ischemia | 171–171 | 155–155 | 12 | 26 | 264 |
| Crohn's Disease | 171–172 | 155–156 | 13 | 29 | 199 |
| Chronic Constipation | 172–172 | 156–156 | 13 | 27 | 366 |
| Irritable Bowel Syndrome | 172–173 | 156–157 | 13 | 27 | 302 |
| Diverticular Disease of the Colon | 173–174 | 157–158 | 13 | 27 | 262 |
| Carcinoma of the Colon | 174–174 | 158–158 | 12 | 24 | 300 |
| Gastritis and Duodenitis | 174–174 | 158–158 | 1 | 3 | 1 |
| Dyspepsia and Other Dysfunctional Disorders in Stomach with Pain | 174–174 | 158–158 | 1 | 3 | 3 |
| Radiation Enterocolitis | 174–174 | 158–158 | 1 | 3 | 1 |
| Ulcerative Colitis and Other Chronic Colitis and Other Ulcer | 174–174 | 158–158 | 1 | 3 | 1 |
| Post-Gastric Surgery Syndrome, Dumping | 175–175 | 159–159 | 1 | 3 | 3 |
| Chronic Pancreatitis | 175–175 | 159–159 | 1 | 3 | 1 |
| Recurrent Abdominal Pain in Children | 175–175 | 159–159 | 14 | 31 | 232 |
| Carcinoma of the Liver or Biliary System | 175–175 | 159–159 | 1 | 3 | 1 |
| Carcinoma of the Kidney (Grawitz Carcinoma) | 175–175 | 159–159 | 1 | 3 | 1 |
| Familial Mediterranean Fever (FMF) | 176–176 | 160–160 | 13 | 27 | 310 |
| Abdominal Migraine | 176–177 | 160–161 | 13 | 27 | 236 |
| Porphyria—Hepatic Porphyrias | 177–177 | 161–161 | 0 | 3 | 56 |
| Intermittent Acute Porphyria (IAP) | 177–178 | 161–162 | 14 | 29 | 324 |
| Hereditary Coproporphyria (HCP) | 178–178 | 162–162 | 8 | 17 | 92 |
| Variegate Porphyria (VP) | 178–178 | 162–162 | 10 | 23 | 175 |
| Muscle Tension Pain | 179–179 | 163–163 | 1 | 4 | 9 |
| Delusional or Hallucinatory Pain | 179–179 | 163–163 | 1 | 4 | 5 |
| Conversion Pain | 179–179 | 163–163 | 2 | 7 | 63 |
| Associated with Depression | 179–179 | 163–163 | 2 | 6 | 39 |
| Abdominal Pain—Visceral Pain Referred to the Abdomen | 179–179 | 163–163 | 0 | 5 | 19 |
| Mittelschmerz | 179–180 | 163–164 | 12 | 25 | 500 |
| Secondary Dysmenorrhea | 180–181 | 164–165 | 6 | 36 | 1118 |
| Primary Dysmenorrhea | 182–182 | 166–166 | 14 | 31 | 651 |
| Endometriosis | 183–184 | 167–168 | 12 | 26 | 809 |
| Posterior Parametritis | 184–184 | 168–168 | 8 | 18 | 264 |
| Tuberculous Salpingitis | 184–185 | 168–169 | 15 | 33 | 848 |
| Ovarian Pain | 185–186 | 169–170 | 4 | 12 | 286 |
| Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) | 186–187 | 170–171 | 10 | 32 | 1055 |
| Pain from Urinary Tract | 187–187 | 171–171 | 1 | 3 | 3 |
| Pain of Vaginismus or Dyspareunia | 187–187 | 171–171 | 1 | 3 | 1 |
| Carcinoma of the Bladder | 187–187 | 171–171 | 1 | 3 | 1 |
| Neuralgia of Iliohypogastric, Ilio-inguinal, or Genito-Femoral Nerves | 188–188 | 172–172 | 0 | 1 | 0 |
| Testicular Pain | 188–188 | 172–172 | 12 | 31 | 541 |
| Rectal, Perineal, and Genital Pain of Psychological Origin | 189–189 | 173–173 | 1 | 8 | 90 |
| Pain of Hemorrhoids | 189–189 | 173–173 | 0 | 2 | 2 |
| Proctalgia Fugax | 189–190 | 173–174 | 17 | 39 | 442 |
| Ulcer of Anus or Rectum | 190–190 | 174–174 | 1 | 3 | 2 |
| Injury of External Genitalia | 190–190 | 174–174 | 1 | 3 | 2 |
| Carcinoma of the Prostate | 190–190 | 174–174 | 1 | 3 | 1 |
| Lumbar Spinal or Radicular Pain Attributable to a Fracture | 191–191 | 175–175 | 4 | 20 | 122 |
| Lumbar Spinal or Radicular Pain Attributable to an Infection | 191–192 | 175–176 | 4 | 28 | 214 |
| Lumbar Spinal or Radicular Pain Attributable to a Neoplasm | 192–192 | 176–176 | 4 | 35 | 210 |
| Lumbar Spinal or Radicular Pain Attributable to Metabolic Bone Disease | 192–193 | 176–177 | 4 | 21 | 110 |
| Lumbar Spinal or Radicular Pain Attributable to Arthritis | 193–193 | 177–177 | 6 | 25 | 222 |
| Lumbar Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | 193–193 | 177–177 | 5 | 11 | 88 |
| Pseudarthrosis of a Transitional Vertebra | 193–194 | 177–178 | 7 | 15 | 149 |
| Pain Referred From Abdominal Viscera or Vessels and Perceived as Lumbar Spinal Pain | 194–194 | 178–178 | 4 | 20 | 101 |
| Lumbar Spinal Pain of Unknown or Uncertain Origin | 194–194 | 178–178 | 5 | 12 | 187 |
| Upper Lumbar Spinal Pain of Unknown or Uncertain Origin | 194–195 | 178–179 | 6 | 12 | 41 |
| Lower Lumbar Spinal Pain of Unknown or Uncertain Origin | 195–195 | 179–179 | 6 | 13 | 42 |
| Lumbosacral Spinal Pain of Unknown or Uncertain Origin | 195–195 | 179–179 | 6 | 12 | 38 |
| Lumbar Spinal or Radicular Pain after Failed Spinal Surgery | 195–195 | 179–179 | 6 | 15 | 207 |
| Lumbar Discogenic Pain | 196–196 | 180–180 | 7 | 28 | 420 |
| Internal Disk Disruption | 196–197 | 180–181 | 6 | 21 | 315 |
| Lumbar Zygapophysial Joint Pain | 197–198 | 181–182 | 7 | 42 | 659 |
| Lumbar Muscle Sprain | 198–198 | 182–182 | 7 | 26 | 302 |
| Lumbar Trigger Point Syndrome | 198–199 | 182–183 | 7 | 26 | 282 |
| Lumbar Muscle Spasm | 199–199 | 183–183 | 7 | 25 | 266 |
| Lumbar Segmental Dysfunction | 199–200 | 183–184 | 6 | 17 | 261 |
| Lumbar Ligament Sprain | 200–200 | 184–184 | 6 | 17 | 322 |
| Sprain of the Anulus Fibrosus | 200–201 | 184–185 | 7 | 18 | 295 |
| Interspinous Pseudarthrosis (Kissing Spines, Baastrup’s Disease) | 201–201 | 185–185 | 7 | 15 | 170 |
| Lumbar Instability | 201–202 | 185–186 | 7 | 20 | 392 |
| Spondylolysis | 202–202 | 186–186 | 6 | 14 | 194 |
| Prolapsed Intervertebral Disk | 202–202 | 186–186 | 1 | 3 | 4 |
| Sacral Spinal or Radicular Pain Attributable to a Fracture | 203–203 | 187–187 | 4 | 9 | 55 |
| Sacral Spinal or Radicular Pain Attributable to an Infection | 203–203 | 187–187 | 4 | 23 | 173 |
| Sacral Spinal or Radicular Pain Attributable to a Neoplasm | 203–204 | 187–188 | 4 | 31 | 177 |
| Sacral Spinal or Radicular Pain Attributable to Metabolic Bone Disease | 204–204 | 188–188 | 4 | 21 | 109 |
| Sacral Spinal or Radicular Pain Attributable to Arthritis | 204–204 | 188–188 | 5 | 20 | 92 |
| Spinal Stenosis: Cauda Equina Lesion | 204–205 | 188–189 | 12 | 29 | 489 |
| Sacral Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | 205–205 | 189–189 | 5 | 11 | 87 |
| Pain Referred from Abdominal or Pelvic Viscera or Vessels Perceived as Sacral Spinal Pain | 206–206 | 190–190 | 4 | 13 | 108 |
| Sacral Spinal Pain of Unknown or Uncertain Origin | 206–206 | 190–190 | 6 | 15 | 179 |
| Sacroiliac Joint Pain | 206–207 | 190–191 | 7 | 19 | 288 |
| Coccygeal Pain of Unknown or Uncertain Origin | 207–207 | 191–191 | 6 | 15 | 177 |
| Posterior Sacrococcygeal Joint Pain | 207–207 | 191–191 | 5 | 13 | 80 |
| Generalized Spinal Pain Attributable to Multiple Fractures | 208–208 | 192–192 | 4 | 9 | 58 |
| Generalized Spinal Pain Attributable to Disseminated Neoplastic Disease | 208–208 | 192–192 | 4 | 15 | 109 |
| Generalized Spinal Pain Attributable to Metabolic Bone Disease | 208–208 | 192–192 | 4 | 20 | 94 |
| Generalized Spinal Pain Attributable to Arthritis | 208–209 | 192–193 | 4 | 17 | 69 |
| Ankylosing Spondylitis | 209–209 | 193–193 | 16 | 33 | 248 |
| Back Pain of Other Visceral or Neurological Origin Involving the Spine | 209–209 | 193–193 | 0 | 1 | 0 |
| Carcinoma of the Rectum | 209–209 | 193–193 | 1 | 5 | 8 |
| Tumor Infiltration of the Lumbosacral Plexus | 210–210 | 194–194 | 10 | 22 | 332 |
| Tumor Infiltration of the Sacrum and Sacral Nerves | 210–211 | 194–195 | 12 | 30 | 325 |
| Low Back Pain of Psychological Origin with Spinal Referral | 211–211 | 195–195 | 1 | 8 | 11 |
| Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica) | 213–213 | 197–197 | 9 | 20 | 215 |
| Obturator Neuralgia | 213–214 | 197–198 | 14 | 33 | 209 |
| Femoral Neuralgia | 214–214 | 198–198 | 14 | 32 | 253 |
| Sciatica Neuralgia | 214–215 | 198–199 | 15 | 31 | 250 |
| Interdigital Neuralgia of the Foot (Morton’s Metatarsalgia) | 215–215 | 199–199 | 12 | 25 | 189 |
| Injection Neuropathy | 215–215 | 199–199 | 1 | 3 | 1 |
| Gluteal Syndromes | 215–216 | 199–200 | 10 | 21 | 294 |
| Piriformis Syndrome | 216–217 | 200–201 | 14 | 39 | 986 |
| Painful Legs and Moving Toes | 218–218 | 202–202 | 9 | 21 | 286 |
| Metastatic Disease | 218–218 | 202–202 | 9 | 19 | 272 |
| Peroneal Muscular Atrophy (Charcot-Marie-Tooth Disease) | 219–219 | 203–203 | 11 | 26 | 370 |
| Ischial Bursitis | 220–220 | 204–204 | 11 | 28 | 126 |
| Trochanteric Bursitis | 220–220 | 204–204 | 13 | 26 | 222 |
| Osteoarthritis of the Hip | 221–221 | 205–205 | 3 | 8 | 55 |
| Spinal Stenosis | 221–221 | 205–205 | 1 | 4 | 4 |
| Osteoarthritis of the Knee | 221–221 | 205–205 | 4 | 9 | 47 |
| Night Cramps | 221–221 | 205–205 | 8 | 18 | 108 |
| Plantar Fasciitis | 221–222 | 205–206 | 10 | 21 | 102 |

## 2. Đối chiếu mục lục

Trang mục lục: PDF [5, 6] · trang PDF = trang in +16

| Mục lục | Cấp | Tr.in (mục lục) | Nút trong cây | Trang khớp |
|---|---|---|---|---|
| List of Items Usually Provided in Detailed Descriptions of Pain Syndromes | chapter | 38 | ✗ **không tìm thấy** | - |
| A. Relatively Generalized Syndromes | part | 39 | ✓ A. Relatively generalized syndromes | ✓ PDF 55 |
| I. Relatively Generalized Syndromes | chapter | 39 | ✓ GROUP I: Relatively generalized syndromes | ✓ PDF 55 |
| B. Relatively Localized Syndromes of the Head and Neck | part | 59 | ✓ B. Relatively localized syndromes of the head and neck | ✓ PDF 75 |
| II. Neuralgias of the Head and Face | chapter | 59 | ✓ GROUP II: Neuralgias of the head and face | ✓ PDF 75 |
| III. Craniofacial Pain of Musculoskeletal Origin | chapter | 68 | ✓ GROUP III: Craniofacial pain of musculoskeletal origin | ✓ PDF 84 |
| IV. Lesions of the Ear, Nose, and Oral Cavity | chapter | 72 | ✓ GROUP IV: Lesions of the ear, nose, and oral cavity | ✓ PDF 88 |
| V. Primary Headache Syndromes, Vascular Disorders, and Cerebrospinal Fluid Syndromes | chapter | 77 | ✓ GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes | ✓ PDF 93 |
| Headache Crosswalk | chapter | 90 | ✓ Headache crosswalk | ✓ PDF 106 |
| VI. Pain of Psychological Origin in the Head, Face, and Neck | chapter | 93 | ✓ GROUP VI: Pain of psychological origin in the head, face, and neck | ✓ PDF 109 |
| VII. Suboccipital and Cervical Musculoskeletal Disorders | chapter | 93 | ✓ GROUP VII: Suboccipital and cervical musculoskeletal disorders | ✓ PDF 109 |
| VIII. Visceral Pain in the Neck | chapter | 98 | ✓ GROUP VIII: Visceral pain in the neck | ✓ PDF 114 |
| C. Spinal Pain, Section 1: Spinal and Radicular Pain Syndromes | part | 101 | ✓ C. Spinal pain, section 1: spinal and radicular pain syndromes | ✓ PDF 117 |
| D. Spinal Pain, Section 2: Spinal and Radicular Pain Syndromes of the Cervical and Thoracic Regions | part | 103 | ✓ D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions | ✓ PDF 119 |
| IX. Cervical Spinal or Radicular Pain Syndromes | chapter | 103 | ✓ GROUP IX: Cervical or radicular spinal pain syndromes | ✓ PDF 119 |
| X. Thoracic Spinal or Radicular Pain Syndromes | chapter | 112 | ✓ GROUP X: Thoracic spinal or radicular pain syndromes | ✓ PDF 128 |
| E. Local Syndromes of the Upper Limbs and Relatively Generalized Syndromes of the Upper and Lower Limbs | part | 121 | ✓ E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs | ✓ PDF 137 |
| XI. Pain in the Shoulder, Arm, and Hand | chapter | 121 | ✓ GROUP XI: Pain in the shoulder, arm, and hand | ✓ PDF 137 |
| XII. Vascular Disease of the Limbs | chapter | 128 | ✓ GROUP XII: Vascular disease of the limbs | ✓ PDF 144 |
| XIII. Collagen Disease of the Limbs | chapter | 131 | ✓ GROUP XIII: Collagen disease of the limbs | ✓ PDF 147 |
| XIV. Vasodilating Functional Disease of the Limbs | chapter | 132 | ✓ GROUP XIV: Vasodilating functional disease of the limbs | ✓ PDF 148 |
| XV. Arterial Insufficiency in the Limbs | chapter | 134 | ✓ GROUP XV: Arterial insufficiency in the limbs | ✓ PDF 150 |
| XVI. Pain of Psychological Origin in the Lower Limbs | chapter | 136 | ✓ GROUP XVI: Pain of psychological origin in the lower limbs | ✓ PDF 152 |
| F. Visceral and Other Syndromes of the Trunk Apart from Spinal and Radicular Pain | part | 137 | ✓ F. Visceral and other syndromes of the trunk apart from spinal and radicular pain | ✓ PDF 153 |
| XVII. Visceral and Other Chest Pain | chapter | 137 | ✓ GROUP XVII: Visceral and other chest pain | ✓ PDF 153 |
| XVIII. Chest Pain of Psychological Origin | chapter | 145 | ✓ GROUP XVIII: Chest pain of psychological origin | ✓ PDF 161 |
| XIX. Chest Pain Referred from Abdomen or Gastrointestinal Tract | chapter | 146 | ✓ GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract | ✓ PDF 162 |
| XX. Abdominal Pain of Neurological Origin | chapter | 149 | ✓ GROUP XX: Abdominal pain of neurological origin | ✓ PDF 165 |
| XXI. Abdominal Pain of Visceral Origin | chapter | 151 | ✓ GROUP XXI: Abdominal pain of visceral origin | ✓ PDF 167 |
| XXII. Abdominal Pain Syndromes of Generalized Diseases | chapter | 160 | ✓ GROUP XXII: Abdominal pain syndromes of generalized diseases | ✓ PDF 176 |
| XXIII. Abdominal Pain of Psychological Origin | chapter | 163 | ✓ GROUP XXIII: Abdominal pain of psychological origin | ✓ PDF 179 |
| XXIV. Diseases of the Bladder, Uterus, Ovaries, and Adnexa | chapter | 163 | ✓ GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa | ✓ PDF 179 |
| XXV. Pain in the Rectum, Perineum, and External Genitalia | chapter | 172 | ✓ GROUP XXV: Pain in the rectum, perineum, and external genitalia | ✓ PDF 188 |
| G. Spinal Pain, Section 3: Spinal and Radicular Pain Syndromes of the Lumbar, Sacral, and Coccygeal Regions | part | 175 | ✓ G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions | ✓ PDF 191 |
| XXVI. Lumbar Spinal or Radicular Pain Syndromes | chapter | 175 | ✓ GROUP XXVI: Lumbar or radicular spinal pain syndromes | ✓ PDF 191 |
| XXVII. Sacral Spinal or Radicular Pain Syndromes | chapter | 187 | ✓ GROUP XXVII: Sacral spinal or radicular pain syndromes | ✓ PDF 203 |
| XXVIII. Coccygeal Pain Syndromes | chapter | 191 | ✓ GROUP XXVIII: Coccygeal pain syndromes | ✓ PDF 207 |
| XXIX. Diffuse or Generalized Spinal Pain | chapter | 192 | ✓ GROUP XXIX: Diffuse or generalized spinal pain | ✓ PDF 208 |
| XXX. Low Back Pain of Psychological Origin with Spinal Referral | chapter | 195 | ✓ GROUP XXX: Low back pain of psychological origin with spinal referral | ✓ PDF 211 |
| H. Local Syndromes of the Lower Limbs | part | 197 | ✓ H. Local syndromes of the lower limbs | ✓ PDF 213 |
| XXXI. Local Syndromes in the Leg or Foot: Pain of Neurological Origin | chapter | 197 | ✓ GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin | ✓ PDF 213 |
| XXXII. Pain Syndromes of the Hip and Thigh of Musculoskeletal Origin | chapter | 204 | ✓ GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin | ✓ PDF 220 |
| XXXIII. Musculoskeletal Syndromes of the Leg | chapter | 205 | ✓ GROUP XXXIII: Musculoskeletal syndromes of the leg | ✓ PDF 221 |

Nút chương/bệnh trong cây nhưng **không có trong mục lục**: `Items usually provided in descriptions`, `Peripheral Neuropathy`, `Stump Pain`, `Phantom Pain`, `Complex Regional Pain Syndromes (CRPS)`, `Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy)`, `Complex Regional Pain Syndrome, Type II (Causalgia)`, `Central Pain`, `Syndrome of Syringomyelia`, `Polymyalgia Rheumatica`, `Fibromyalgia (or Fibrositis)`, `Note: Specific Myofascial Pain Syndromes`, `Rheumatoid Arthritis`, `Osteoarthritis`, `Calcium Pyrophosphate Dihydrate Deposition Disease (CPPD)`, `Gout`, `Hemophilic Arthropathy`, `Burns`, `Pain of Psychological Origin: Muscle Tension Pain`, `Pain of Psychological Origin: Delusional or Hallucinatory`, `Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal`, `Pain of Psychological Origin: Associated with Depression`, `A Note on Factitious Illness and Malingering`, `Regional Sprains or Strains`, `Sickle Cell Arthropathy`, `Purpuric Arthropathy`, `Stiff Man Syndrome`, `Paralysis Agitans`, `Epilepsy`, `Polyarteritis Nodosa`, `Psoriatic Arthropathy and Other Secondary Arthropathies`, `Painful Scar`, `Systemic Lupus Erythematosis, Systemic Sclerosis and Fibrosclerosis, Polymyositis, and Dermatomyositis`, `Infective Arthropathies`, `Traumatic Arthropathy`, `Osteomyelitis`, `Osteitis Deformans`, `Osteochondritis`, `Osteoporosis`, `Muscle Spasm`, `Local Pain, No Cause Specified`, `Guillain-Barre Syndrome`, `Trigeminal Neuralgia (Tic Douloureux)`, `Secondary Neuralgia (Trigeminal) from Central Nervous System Lesions`, `Secondary Trigeminal Neuralgia from Facial Trauma`, `Acute Herpes Zoster (Trigeminal)`, `Postherpetic Neuralgia (Trigeminal)`, `Geniculate Neuralgia (VIIth Cranial Nerve): Ramsay Hunt Syndrome`, `Neuralgia of the Nervus Intermedius`, `Glossopharyngeal Neuralgia (IXth Cranial Nerve)`, `Neuralgia of the Superior Laryngeal Nerve (Vagus Nerve Neuralgia)`, `Occipital Neuralgia`, `Hypoglossal Neuralgia`, `Glossopharyngeal Pain from Trauma`, `Hypoglossal Pain from Trauma`, `Tolosa-Hunt Syndrome (Painful Ophthalmoplegia)`, `SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing)`, `Raeder’s Syndrome (Raeder’s Paratrigeminal Syndrome)`, `Acute Tension Headache`, `Tension Headache: Chronic Form (Scalp Muscle Contraction Headache)`, `Temporomandibular Pain and Dysfunction Syndrome`, `Osteoarthritis of the Temporomandibular Joint`, `Rheumatoid Arthritis of the Temporomandibular Joint`, `Dystonic Disorders, Facial Dyskinesia`, `Crushing Injury of Head or Face`, `Maxillary Sinusitis`, `Odontalgia: Toothache 1. Due to Dentino-Enamel Defects`, `Odontalgia: Toothache 2. Pulpitis`, `Odontalgia: Toothache 3. Periapical Periodontitis and Abscess`, `Odontalgia: Toothache 4. Tooth Pain Not Associated with Lesions (Atypical Odontalgia)`, `Glossodynia and Sore Mouth`, `Cracked Tooth Syndrome`, `Dry Socket`, `Gingival Disease, Inflammatory`, `Toothache, Cause Unknown`, `Diseases of the Jaw, Inflammatory Conditions`, `Other and Unspecified Pain in Jaws`, `Frostbite of Face`, `Classic Migraine (Migraine with Aura)`, `Common Migraine (Migraine without Aura)`, `Migraine Variants`, `Carotidynia`, `Mixed Headache`, `Cluster Headache`, `Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety)`, `Chronic Paroxysmal Hemicrania (CPH) (Remitting Form or Variety)`, `Chronic Cluster Headache`, `Cluster-Tic Syndrome`, `Post-traumatic Headache`, `The Syndrome of “Jabs and Jolts”`, `Temporal Arteritis (Giant Cell Arteritis)`, `Headache Associated with Low CSF Pressure`, `Post-Dural Puncture Headache`, `Hemicrania Continua`, `Headache Not Otherwise Specified`, `Delusional or Hallucinatory Pain`, `Hysterical, Conversion, or Hypochondriacal Pain`, `Associated with Depression`, `Stylohyoid Process Syndrome (Eagle’s Syndrome)`, `Cervicogenic Headache`, `Superior Pulmonary Sulcus Syndrome (Pancoast Tumor)`, `Thoracic Outlet Syndrome`, `Cervical Rib or Malformed First Thoracic Rib`, `Pain of Skeletal Metastatic Disease of the Neck, Arm, or Shoulder Girdle`, `Carcinoma of Thyroid`, `Carcinoma of Larynx`, `Tuberculosis of Larynx`, `Chronic Pharyngitis`, `Carcinoma of Pharynx`, `Cervical Spinal or Radicular Pain Attributable to a Fracture`, `Cervical Spinal or Radicular Pain Attributable to an Infection`, `Cervical Spinal or Radicular Pain Attributable to a Neoplasm`, `Cervical Spinal or Radicular Pain Attributable to Metabolic Bone Disease`, `Cervical Spinal or Radicular Pain Attributable to Arthritis`, `Cervical Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly`, `Cervical Spinal Pain of Unknown or Uncertain Origin`, `Upper Cervical Spinal Pain of Unknown or Uncertain Origin`, `Lower Cervical Spinal Pain of Unknown or Uncertain Origin`, `Cervico-Thoracic Spinal Pain of Unknown or Uncertain Origin`, `Acceleration-Deceleration Injury of the Neck (Cervical Sprain)`, `Torticollis (Spasmodic Torticollis)`, `Cervical Discogenic Pain`, `Cervical Zygapophysial Joint Pain`, `Cervical Muscle Sprain`, `Cervical Trigger Point Syndrome`, `Alar Ligament Sprain`, `Cervical Segmental Dysfunction`, `Radicular Pain Attributable to a Prolapsed Cervical Disk`, `Traumatic Avulsion of Nerve Roots`, `Thoracic Spinal or Radicular Pain Attributable to a Fracture`, `Thoracic Spinal or Radicular Pain Attributable to an Infection`, `Thoracic Spinal or Radicular Pain Attributable to a Neoplasm`, `Thoracic Spinal or Radicular Pain Attributable to Metabolic Bone Disease`, `Thoracic Spinal or Radicular Pain Attributable to Arthritis`, `Thoracic Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly`, `Pain Referred from Thoracic Viscera or Vessels and Perceived as Thoracic Spinal Pain`, `Thoracic Spinal Pain of Unknown or Uncertain Origin`, `Upper Thoracic Spinal Pain of Unknown or Uncertain Origin`, `Midthoracic Spinal Pain of Unknown or Uncertain Origin`, `Lower Thoracic Spinal Pain of Unknown or Uncertain Origin`, `Thoracolumbar Spinal Pain of Unknown or Uncertain Origin`, `Thoracic Discogenic Pain`, `Thoracic Zygapophysial Joint Pain`, `Costo-Transverse Joint Pain`, `Thoracic Muscle Sprain`, `Thoracic Trigger Point Syndrome`, `Thoracic Muscle Spasm`, `Thoracic Segmental Dysfunction`, `Radicular Pain Attributable to a Prolapsed Thoracic Disk`, `Tumors of the Brachial Plexus`, `Chemical Irritation of the Brachial Plexus`, `Traumatic Avulsion of the Brachial Plexus`, `Postradiation Pain of the Brachial Plexus`, `Painful Arms and Moving Fingers`, `Brachial Neuritis (Brachial Neuropathy, Neuralgic Amyotrophy, Parsonage-Turner Syndrome)`, `Bicipital Tendinitis`, `Subacromial Bursitis (Subdeltoid Bursitis, Supraspinatus Tendinitis)`, `Rotator Cuff Tear—Partial or Complete`, `Adhesive Capsulitis and Frozen Shoulder`, `Lateral Epicondylitis (Tennis Elbow)`, `Medial Epicondylitis (Golfer’s Elbow)`, `DeQuervain’s Tenosynovitis`, `Osteoarthritis of the Hands`, `Cubital Tunnel Syndrome`, `Carpal Tunnel Syndrome`, `Pain of Psychological Origin in the Shoulder and Arm`, `Crush Injury of Upper Limbs`, `Pain in a Limb or Limbs, Not Otherwise Specified`, `Raynaud’s Disease`, `Raynaud’s Phenomenon`, `Frostbite and Cold Injury`, `Erythema Pernio (Chilblains)`, `Acrocyanosis`, `Livedo Reticularis`, `Volkmann’s Ischemic Contracture`, `Scleroderma`, `Ergotism`, `Erythromelalgia`, `Thromboangiitis Obliterans`, `Chronic Venous Insufficiency`, `Intermittent Claudication (XV-1) and Rest Pain`, `Gangrene Due to Arterial Insufficiency`, `Acute Herpes Zoster`, `Postherpetic Neuralgia`, `Postinfectious and Segmental Peripheral Neuralgia`, `Angina Pectoris`, `Myocardial Infarction`, `Pericarditis`, `Aneurysm of the Aorta`, `Diseases of the Diaphragm`, `Carcinoma of Esophagus`, `Slipping Rib Syndrome`, `Postmastectomy Pain Syndrome: Chronic Nonmalignant`, `Late Postmastectomy Pain or Regional Carcinoma`, `Post-thoracotomy Pain Syndrome`, `Internal Mammary Artery Syndrome`, `Tietze’s Syndrome— Costo-Chondritis`, `Fractured Ribs or Sternum`, `Xiphoidalgia Syndrome`, `Carcinoma of the Lung or Pleura`, `Muscle Tension Pain`, `Delusional Pain`, `Conversion Pain`, `With Depression`, `Subphrenic Abscess`, `Herniated Abdominal Organs`, `Esophageal Motility Disorders`, `Esophagitis`, `Reflux Esophagitis with Peptic Ulceration`, `Gastric Ulcer with Chest Pain`, `Duodenal Ulcer with Chest Pain`, `Thoracic Visceral Disease with Pain Referred to Abdomen`, `Acute Herpes Zoster`, `Postherpetic Neuralgia`, `Segmental or Intercostal Neuralgia`, `Twelfth Rib Syndrome`, `Abdominal Cutaneous Nerve Entrapment Syndrome`, `Cardiac Failure`, `Gallbladder Disease`, `Post-cholecystectomy Syndrome`, `Chronic Gastric Ulcer`, `Chronic Duodenal Ulcer`, `Carcinoma of the Stomach`, `Carcinoma of the Pancreas`, `Chronic Mesenteric Ischemia`, `Crohn's Disease`, `Chronic Constipation`, `Irritable Bowel Syndrome`, `Diverticular Disease of the Colon`, `Carcinoma of the Colon`, `Gastritis and Duodenitis`, `Dyspepsia and Other Dysfunctional Disorders in Stomach with Pain`, `Radiation Enterocolitis`, `Ulcerative Colitis and Other Chronic Colitis and Other Ulcer`, `Post-Gastric Surgery Syndrome, Dumping`, `Chronic Pancreatitis`, `Recurrent Abdominal Pain in Children`, `Carcinoma of the Liver or Biliary System`, `Carcinoma of the Kidney (Grawitz Carcinoma)`, `Familial Mediterranean Fever (FMF)`, `Abdominal Migraine`, `Porphyria—Hepatic Porphyrias`, `Intermittent Acute Porphyria (IAP)`, `Hereditary Coproporphyria (HCP)`, `Variegate Porphyria (VP)`, `Muscle Tension Pain`, `Delusional or Hallucinatory Pain`, `Conversion Pain`, `Associated with Depression`, `Abdominal Pain—Visceral Pain Referred to the Abdomen`, `Mittelschmerz`, `Secondary Dysmenorrhea`, `Primary Dysmenorrhea`, `Endometriosis`, `Posterior Parametritis`, `Tuberculous Salpingitis`, `Ovarian Pain`, `Chronic Pelvic Pain Without Obvious Pathology (CPPWOP)`, `Pain from Urinary Tract`, `Pain of Vaginismus or Dyspareunia`, `Carcinoma of the Bladder`, `Neuralgia of Iliohypogastric, Ilio-inguinal, or Genito-Femoral Nerves`, `Testicular Pain`, `Rectal, Perineal, and Genital Pain of Psychological Origin`, `Pain of Hemorrhoids`, `Proctalgia Fugax`, `Ulcer of Anus or Rectum`, `Injury of External Genitalia`, `Carcinoma of the Prostate`, `Lumbar Spinal or Radicular Pain Attributable to a Fracture`, `Lumbar Spinal or Radicular Pain Attributable to an Infection`, `Lumbar Spinal or Radicular Pain Attributable to a Neoplasm`, `Lumbar Spinal or Radicular Pain Attributable to Metabolic Bone Disease`, `Lumbar Spinal or Radicular Pain Attributable to Arthritis`, `Lumbar Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly`, `Pseudarthrosis of a Transitional Vertebra`, `Pain Referred From Abdominal Viscera or Vessels and Perceived as Lumbar Spinal Pain`, `Lumbar Spinal Pain of Unknown or Uncertain Origin`, `Upper Lumbar Spinal Pain of Unknown or Uncertain Origin`, `Lower Lumbar Spinal Pain of Unknown or Uncertain Origin`, `Lumbosacral Spinal Pain of Unknown or Uncertain Origin`, `Lumbar Spinal or Radicular Pain after Failed Spinal Surgery`, `Lumbar Discogenic Pain`, `Internal Disk Disruption`, `Lumbar Zygapophysial Joint Pain`, `Lumbar Muscle Sprain`, `Lumbar Trigger Point Syndrome`, `Lumbar Muscle Spasm`, `Lumbar Segmental Dysfunction`, `Lumbar Ligament Sprain`, `Sprain of the Anulus Fibrosus`, `Interspinous Pseudarthrosis (Kissing Spines, Baastrup’s Disease)`, `Lumbar Instability`, `Spondylolysis`, `Prolapsed Intervertebral Disk`, `Sacral Spinal or Radicular Pain Attributable to a Fracture`, `Sacral Spinal or Radicular Pain Attributable to an Infection`, `Sacral Spinal or Radicular Pain Attributable to a Neoplasm`, `Sacral Spinal or Radicular Pain Attributable to Metabolic Bone Disease`, `Sacral Spinal or Radicular Pain Attributable to Arthritis`, `Spinal Stenosis: Cauda Equina Lesion`, `Sacral Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly`, `Pain Referred from Abdominal or Pelvic Viscera or Vessels Perceived as Sacral Spinal Pain`, `Sacral Spinal Pain of Unknown or Uncertain Origin`, `Sacroiliac Joint Pain`, `Coccygeal Pain of Unknown or Uncertain Origin`, `Posterior Sacrococcygeal Joint Pain`, `Generalized Spinal Pain Attributable to Multiple Fractures`, `Generalized Spinal Pain Attributable to Disseminated Neoplastic Disease`, `Generalized Spinal Pain Attributable to Metabolic Bone Disease`, `Generalized Spinal Pain Attributable to Arthritis`, `Ankylosing Spondylitis`, `Back Pain of Other Visceral or Neurological Origin Involving the Spine`, `Carcinoma of the Rectum`, `Tumor Infiltration of the Lumbosacral Plexus`, `Tumor Infiltration of the Sacrum and Sacral Nerves`, `Low Back Pain of Psychological Origin with Spinal Referral`, `Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica)`, `Obturator Neuralgia`, `Femoral Neuralgia`, `Sciatica Neuralgia`, `Interdigital Neuralgia of the Foot (Morton’s Metatarsalgia)`, `Injection Neuropathy`, `Gluteal Syndromes`, `Piriformis Syndrome`, `Painful Legs and Moving Toes`, `Metastatic Disease`, `Peroneal Muscular Atrophy (Charcot-Marie-Tooth Disease)`, `Ischial Bursitis`, `Trochanteric Bursitis`, `Osteoarthritis of the Hip`, `Spinal Stenosis`, `Osteoarthritis of the Knee`, `Night Cramps`, `Plantar Fasciitis`

## 3. Ma trận bệnh × loại mục

| Bệnh | definition | cause | pathophysiology | symptom | paraclinical | diagnosis | differential_diagnosis | treatment | complication | prognosis | site | body_system | code | disability | references |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Peripheral Neuropathy | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Stump Pain | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | — |
| Phantom Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Complex Regional Pain Syndromes (CRPS) | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Complex Regional Pain Syndrome, Type II (Causalgia) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | — |
| Central Pain | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Syndrome of Syringomyelia | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Polymyalgia Rheumatica | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | — | ✓ |
| Fibromyalgia (or Fibrositis) | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Note: Specific Myofascial Pain Syndromes | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Rheumatoid Arthritis | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Osteoarthritis | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Calcium Pyrophosphate Dihydrate Deposition Disease (CPPD) | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ |
| Gout | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — | ✓ |
| Hemophilic Arthropathy | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Burns | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Pain of Psychological Origin: Muscle Tension Pain | ✓ | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| Pain of Psychological Origin: Delusional or Hallucinatory | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | ✓ | — | ✓ | — | ✓ | ✓ | — |
| Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal | ✓ | — | — | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Pain of Psychological Origin: Associated with Depression | ✓ | ✓ | — | ✓ | — | — | ✓ | ✓ | — | — | ✓ | — | ✓ | ✓ | ✓ |
| A Note on Factitious Illness and Malingering | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Regional Sprains or Strains | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Sickle Cell Arthropathy | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Purpuric Arthropathy | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Stiff Man Syndrome | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Paralysis Agitans | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Epilepsy | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Polyarteritis Nodosa | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Psoriatic Arthropathy and Other Secondary Arthropathies | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Painful Scar | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Systemic Lupus Erythematosis, Systemic Sclerosis and Fibrosclerosis, Polymyositis, and Dermatomyositis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Infective Arthropathies | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Traumatic Arthropathy | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Osteomyelitis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Osteitis Deformans | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Osteochondritis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Osteoporosis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Muscle Spasm | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Local Pain, No Cause Specified | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Guillain-Barre Syndrome | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — |
| Trigeminal Neuralgia (Tic Douloureux) | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Secondary Neuralgia (Trigeminal) from Central Nervous System Lesions | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Secondary Trigeminal Neuralgia from Facial Trauma | ✓ | — | ✓ | ✓ | — | — | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Acute Herpes Zoster (Trigeminal) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Postherpetic Neuralgia (Trigeminal) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Geniculate Neuralgia (VIIth Cranial Nerve): Ramsay Hunt Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| Neuralgia of the Nervus Intermedius | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Glossopharyngeal Neuralgia (IXth Cranial Nerve) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Neuralgia of the Superior Laryngeal Nerve (Vagus Nerve Neuralgia) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| Occipital Neuralgia | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Hypoglossal Neuralgia | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Glossopharyngeal Pain from Trauma | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Hypoglossal Pain from Trauma | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Tolosa-Hunt Syndrome (Painful Ophthalmoplegia) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing) | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Raeder’s Syndrome (Raeder’s Paratrigeminal Syndrome) | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Acute Tension Headache | ✓ | — | ✓ | ✓ | — | — | — | — | — | — | — | — | ✓ | — | ✓ |
| Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Temporomandibular Pain and Dysfunction Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Osteoarthritis of the Temporomandibular Joint | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Rheumatoid Arthritis of the Temporomandibular Joint | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Dystonic Disorders, Facial Dyskinesia | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Crushing Injury of Head or Face | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Maxillary Sinusitis | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Odontalgia: Toothache 1. Due to Dentino-Enamel Defects | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Odontalgia: Toothache 2. Pulpitis | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Odontalgia: Toothache 3. Periapical Periodontitis and Abscess | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Odontalgia: Toothache 4. Tooth Pain Not Associated with Lesions (Atypical Odontalgia) | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Glossodynia and Sore Mouth | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| Cracked Tooth Syndrome | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Dry Socket | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Gingival Disease, Inflammatory | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Toothache, Cause Unknown | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Diseases of the Jaw, Inflammatory Conditions | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Other and Unspecified Pain in Jaws | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Frostbite of Face | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Classic Migraine (Migraine with Aura) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Common Migraine (Migraine without Aura) | ✓ | — | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | — | ✓ | — | ✓ |
| Migraine Variants | — | — | — | — | — | — | ✓ | — | — | — | — | — | ✓ | — | — |
| Carotidynia | ✓ | — | ✓ | ✓ | — | — | — | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Mixed Headache | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Cluster Headache | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Chronic Paroxysmal Hemicrania (CPH) (Remitting Form or Variety) | ✓ | — | — | ✓ | — | ✓ | ✓ | ✓ | — | — | — | — | ✓ | — | ✓ |
| Chronic Cluster Headache | ✓ | — | — | ✓ | — | ✓ | ✓ | ✓ | — | — | — | — | ✓ | — | ✓ |
| Cluster-Tic Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Post-traumatic Headache | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| The Syndrome of “Jabs and Jolts” | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Temporal Arteritis (Giant Cell Arteritis) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Headache Associated with Low CSF Pressure | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Post-Dural Puncture Headache | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Hemicrania Continua | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Headache Not Otherwise Specified | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Delusional or Hallucinatory Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Hysterical, Conversion, or Hypochondriacal Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Associated with Depression | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Stylohyoid Process Syndrome (Eagle’s Syndrome) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Cervicogenic Headache | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Superior Pulmonary Sulcus Syndrome (Pancoast Tumor) | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Thoracic Outlet Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Cervical Rib or Malformed First Thoracic Rib | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Pain of Skeletal Metastatic Disease of the Neck, Arm, or Shoulder Girdle | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| Carcinoma of Thyroid | ✓ | — | — | ✓ | ✓ | — | — | — | ✓ | — | ✓ | ✓ | ✓ | — | — |
| Carcinoma of Larynx | ✓ | — | — | ✓ | — | ✓ | — | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| Tuberculosis of Larynx | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | — | — | — | ✓ | ✓ | ✓ | — | — |
| Chronic Pharyngitis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Carcinoma of Pharynx | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Cervical Spinal or Radicular Pain Attributable to a Fracture | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Cervical Spinal or Radicular Pain Attributable to an Infection | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Cervical Spinal or Radicular Pain Attributable to a Neoplasm | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Cervical Spinal or Radicular Pain Attributable to Metabolic Bone Disease | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Cervical Spinal or Radicular Pain Attributable to Arthritis | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | ✓ |
| Cervical Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Cervical Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Upper Cervical Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Lower Cervical Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Cervico-Thoracic Spinal Pain of Unknown or Uncertain Origin | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Acceleration-Deceleration Injury of the Neck (Cervical Sprain) | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Torticollis (Spasmodic Torticollis) | ✓ | — | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | ✓ | — | — |
| Cervical Discogenic Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Cervical Zygapophysial Joint Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Cervical Muscle Sprain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Cervical Trigger Point Syndrome | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | — | — | ✓ |
| Alar Ligament Sprain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Cervical Segmental Dysfunction | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Radicular Pain Attributable to a Prolapsed Cervical Disk | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Traumatic Avulsion of Nerve Roots | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Thoracic Spinal or Radicular Pain Attributable to a Fracture | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Thoracic Spinal or Radicular Pain Attributable to an Infection | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Thoracic Spinal or Radicular Pain Attributable to a Neoplasm | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Thoracic Spinal or Radicular Pain Attributable to Metabolic Bone Disease | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Thoracic Spinal or Radicular Pain Attributable to Arthritis | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Thoracic Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Pain Referred from Thoracic Viscera or Vessels and Perceived as Thoracic Spinal Pain | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Thoracic Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Upper Thoracic Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Midthoracic Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Lower Thoracic Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Thoracolumbar Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Thoracic Discogenic Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Thoracic Zygapophysial Joint Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Costo-Transverse Joint Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Thoracic Muscle Sprain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Thoracic Trigger Point Syndrome | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Thoracic Muscle Spasm | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Thoracic Segmental Dysfunction | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Radicular Pain Attributable to a Prolapsed Thoracic Disk | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Tumors of the Brachial Plexus | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Chemical Irritation of the Brachial Plexus | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Traumatic Avulsion of the Brachial Plexus | ✓ | — | ✓ | ✓ | — | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Postradiation Pain of the Brachial Plexus | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Painful Arms and Moving Fingers | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | ✓ |
| Brachial Neuritis (Brachial Neuropathy, Neuralgic Amyotrophy, Parsonage-Turner Syndrome) | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Bicipital Tendinitis | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Subacromial Bursitis (Subdeltoid Bursitis, Supraspinatus Tendinitis) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Rotator Cuff Tear—Partial or Complete | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | — | — |
| Adhesive Capsulitis and Frozen Shoulder | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Lateral Epicondylitis (Tennis Elbow) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | — |
| Medial Epicondylitis (Golfer’s Elbow) | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | — | — | ✓ | — | — | ✓ | — | — |
| DeQuervain’s Tenosynovitis | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Osteoarthritis of the Hands | ✓ | — | — | ✓ | ✓ | — | — | ✓ | — | — | — | ✓ | ✓ | — | — |
| Cubital Tunnel Syndrome | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Carpal Tunnel Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Pain of Psychological Origin in the Shoulder and Arm | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Crush Injury of Upper Limbs | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Pain in a Limb or Limbs, Not Otherwise Specified | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Raynaud’s Disease | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | — |
| Raynaud’s Phenomenon | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — | ✓ | — | — |
| Frostbite and Cold Injury | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Erythema Pernio (Chilblains) | ✓ | — | — | ✓ | — | — | ✓ | — | — | — | ✓ | — | ✓ | — | — |
| Acrocyanosis | ✓ | — | — | ✓ | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Livedo Reticularis | ✓ | — | — | ✓ | — | — | ✓ | — | — | — | ✓ | — | ✓ | — | — |
| Volkmann’s Ischemic Contracture | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Scleroderma | ✓ | — | — | ✓ | — | ✓ | ✓ | — | — | — | — | — | ✓ | — | — |
| Ergotism | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| Erythromelalgia | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | — | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Thromboangiitis Obliterans | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Chronic Venous Insufficiency | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Intermittent Claudication (XV-1) and Rest Pain | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Gangrene Due to Arterial Insufficiency | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Acute Herpes Zoster | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Postherpetic Neuralgia | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Postinfectious and Segmental Peripheral Neuralgia | ✓ | ✓ | — | ✓ | — | — | ✓ | — | — | — | ✓ | ✓ | ✓ | — | — |
| Angina Pectoris | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Myocardial Infarction | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Pericarditis | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Aneurysm of the Aorta | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Diseases of the Diaphragm | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Carcinoma of Esophagus | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Slipping Rib Syndrome | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Postmastectomy Pain Syndrome: Chronic Nonmalignant | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Late Postmastectomy Pain or Regional Carcinoma | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | — |
| Post-thoracotomy Pain Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Internal Mammary Artery Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tietze’s Syndrome— Costo-Chondritis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Fractured Ribs or Sternum | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Xiphoidalgia Syndrome | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | ✓ |
| Carcinoma of the Lung or Pleura | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Muscle Tension Pain | ✓ | — | — | ✓ | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — |
| Delusional Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Conversion Pain | — | — | — | — | — | — | ✓ | — | — | — | — | — | ✓ | — | — |
| With Depression | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Subphrenic Abscess | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Herniated Abdominal Organs | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Esophageal Motility Disorders | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Esophagitis | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | — |
| Reflux Esophagitis with Peptic Ulceration | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Gastric Ulcer with Chest Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Duodenal Ulcer with Chest Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Thoracic Visceral Disease with Pain Referred to Abdomen | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Acute Herpes Zoster | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Postherpetic Neuralgia | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Segmental or Intercostal Neuralgia | — | — | — | — | — | — | ✓ | — | — | — | — | — | ✓ | — | — |
| Twelfth Rib Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Abdominal Cutaneous Nerve Entrapment Syndrome | ✓ | — | — | ✓ | — | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | — |
| Cardiac Failure | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Gallbladder Disease | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Post-cholecystectomy Syndrome | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Chronic Gastric Ulcer | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Chronic Duodenal Ulcer | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Carcinoma of the Stomach | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Carcinoma of the Pancreas | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | — |
| Chronic Mesenteric Ischemia | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Crohn's Disease | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Chronic Constipation | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Irritable Bowel Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Diverticular Disease of the Colon | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Carcinoma of the Colon | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Gastritis and Duodenitis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Dyspepsia and Other Dysfunctional Disorders in Stomach with Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Radiation Enterocolitis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Ulcerative Colitis and Other Chronic Colitis and Other Ulcer | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Post-Gastric Surgery Syndrome, Dumping | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Chronic Pancreatitis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Recurrent Abdominal Pain in Children | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Carcinoma of the Liver or Biliary System | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Carcinoma of the Kidney (Grawitz Carcinoma) | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Familial Mediterranean Fever (FMF) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| Abdominal Migraine | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Porphyria—Hepatic Porphyrias | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Intermittent Acute Porphyria (IAP) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Hereditary Coproporphyria (HCP) | ✓ | — | ✓ | ✓ | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Variegate Porphyria (VP) | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Muscle Tension Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Delusional or Hallucinatory Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Conversion Pain | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | ✓ |
| Associated with Depression | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | ✓ |
| Abdominal Pain—Visceral Pain Referred to the Abdomen | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Mittelschmerz | ✓ | — | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ |
| Secondary Dysmenorrhea | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — |
| Primary Dysmenorrhea | ✓ | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Endometriosis | ✓ | — | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Posterior Parametritis | ✓ | — | ✓ | ✓ | — | — | — | ✓ | — | — | — | ✓ | ✓ | — | ✓ |
| Tuberculous Salpingitis | ✓ | — | ✓ | ✓ | — | ✓ | — | ✓ | — | ✓ | — | — | ✓ | — | ✓ |
| Ovarian Pain | ✓ | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | ✓ |
| Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) | ✓ | — | ✓ | ✓ | — | — | — | ✓ | — | — | ✓ | ✓ | ✓ | — | ✓ |
| Pain from Urinary Tract | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Pain of Vaginismus or Dyspareunia | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Carcinoma of the Bladder | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Neuralgia of Iliohypogastric, Ilio-inguinal, or Genito-Femoral Nerves | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Testicular Pain | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Rectal, Perineal, and Genital Pain of Psychological Origin | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Pain of Hemorrhoids | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Proctalgia Fugax | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ulcer of Anus or Rectum | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Injury of External Genitalia | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Carcinoma of the Prostate | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Lumbar Spinal or Radicular Pain Attributable to a Fracture | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Lumbar Spinal or Radicular Pain Attributable to an Infection | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Lumbar Spinal or Radicular Pain Attributable to a Neoplasm | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Lumbar Spinal or Radicular Pain Attributable to Metabolic Bone Disease | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Lumbar Spinal or Radicular Pain Attributable to Arthritis | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | ✓ |
| Lumbar Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Pseudarthrosis of a Transitional Vertebra | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Pain Referred From Abdominal Viscera or Vessels and Perceived as Lumbar Spinal Pain | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Lumbar Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Upper Lumbar Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Lower Lumbar Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Lumbosacral Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Lumbar Spinal or Radicular Pain after Failed Spinal Surgery | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Lumbar Discogenic Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Internal Disk Disruption | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Lumbar Zygapophysial Joint Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Lumbar Muscle Sprain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Lumbar Trigger Point Syndrome | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | — | — | ✓ |
| Lumbar Muscle Spasm | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Lumbar Segmental Dysfunction | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Lumbar Ligament Sprain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Sprain of the Anulus Fibrosus | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Interspinous Pseudarthrosis (Kissing Spines, Baastrup’s Disease) | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Lumbar Instability | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Spondylolysis | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Prolapsed Intervertebral Disk | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Sacral Spinal or Radicular Pain Attributable to a Fracture | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Sacral Spinal or Radicular Pain Attributable to an Infection | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Sacral Spinal or Radicular Pain Attributable to a Neoplasm | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Sacral Spinal or Radicular Pain Attributable to Metabolic Bone Disease | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Sacral Spinal or Radicular Pain Attributable to Arthritis | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | ✓ |
| Spinal Stenosis: Cauda Equina Lesion | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | — |
| Sacral Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Pain Referred from Abdominal or Pelvic Viscera or Vessels Perceived as Sacral Spinal Pain | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Sacral Spinal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Sacroiliac Joint Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | ✓ |
| Coccygeal Pain of Unknown or Uncertain Origin | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Posterior Sacrococcygeal Joint Pain | ✓ | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Generalized Spinal Pain Attributable to Multiple Fractures | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | — | — | ✓ | — | — |
| Generalized Spinal Pain Attributable to Disseminated Neoplastic Disease | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Generalized Spinal Pain Attributable to Metabolic Bone Disease | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Generalized Spinal Pain Attributable to Arthritis | ✓ | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — |
| Ankylosing Spondylitis | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Back Pain of Other Visceral or Neurological Origin Involving the Spine | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Carcinoma of the Rectum | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Tumor Infiltration of the Lumbosacral Plexus | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Tumor Infiltration of the Sacrum and Sacral Nerves | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Low Back Pain of Psychological Origin with Spinal Referral | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica) | ✓ | — | — | ✓ | — | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | — |
| Obturator Neuralgia | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Femoral Neuralgia | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Sciatica Neuralgia | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Interdigital Neuralgia of the Foot (Morton’s Metatarsalgia) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Injection Neuropathy | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Gluteal Syndromes | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | — | — | — | ✓ | ✓ | ✓ | — | — |
| Piriformis Syndrome | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Painful Legs and Moving Toes | ✓ | — | ✓ | ✓ | — | — | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Metastatic Disease | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | — | ✓ | — | — |
| Peroneal Muscular Atrophy (Charcot-Marie-Tooth Disease) | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | — |
| Ischial Bursitis | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | — |
| Trochanteric Bursitis | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Osteoarthritis of the Hip | ✓ | — | — | ✓ | — | — | — | — | — | — | — | — | ✓ | — | — |
| Spinal Stenosis | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — |
| Osteoarthritis of the Knee | ✓ | — | — | ✓ | — | — | — | — | — | — | — | ✓ | ✓ | — | — |
| Night Cramps | ✓ | — | — | ✓ | — | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | — |
| Plantar Fasciitis | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | — | — |

- Loại mục **chỉ có ở một số bệnh** (P4 phải chấp nhận trường trống): `definition`, `cause`, `pathophysiology`, `symptom`, `paraclinical`, `diagnosis`, `differential_diagnosis`, `treatment`, `complication`, `prognosis`, `site`, `body_system`, `code`, `disability`, `references`
- Loại mục **không bệnh nào có**: `risk_factor`, `prevention`

## 4. Cảnh báo cần người xem

| Mức | Nút | Nội dung |
|---|---|---|
| ℹ | Phần đầu | `other_heading`: có tiêu đề cấp 'other' bị gộp vào nội dung |
| ℹ | Items usually provided in descriptions | `other_heading`: có tiêu đề cấp 'other' bị gộp vào nội dung |
| ⚠ | Items usually provided in descriptions | `unnumbered_chapter`: unnumbered_chapter |
| ⚠ | Items usually provided in descriptions › Definition | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Definition | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Site | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Site | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › System(s) | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › System(s) | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Main Features | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Associated Symptoms — aggravating and relieving agents | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Associated Symptoms — aggravating and relieving agents | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Signs | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Signs | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Laboratory Findings | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Laboratory Findings | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Usual Course | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Complications | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Complications | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Social and Physical Disability | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Social and Physical Disability | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Pathology | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Summary of Essential Features and Diagnostic Criteria | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Summary of Essential Features and Diagnostic Criteria | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Criteria | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Differential Diagnosis | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Differential Diagnosis | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › Code(s) | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | Items usually provided in descriptions › Code(s) | `empty`: nút không có nội dung và không có con |
| ⚠ | Items usually provided in descriptions › References | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Stump Pain | `no_iasp_code`: no_iasp_code |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndromes (CRPS) | `no_code`: no_code |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndromes (CRPS) | `no_iasp_code`: no_iasp_code |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Polymyalgia Rheumatica › Code X32.X3a | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Classification Criteria for Primary and Concomitant Fibromyalgia (from Wolfe et al. 1990) › 1. History of Widespread Pain | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Definition | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Definition › 2. Pain in 11 of 18 Tender Point Sites on Digital Palpation | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Definition | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Code X33.X8a | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Note: Specific Myofascial Pain Syndromes | `no_code`: no_code |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Note: Specific Myofascial Pain Syndromes | `no_iasp_code`: no_iasp_code |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Rheumatoid Arthritis › Code X34.X3a | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteoarthritis › Code X38.X6a | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Gout | `no_iasp_code`: no_iasp_code |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Code X34.XOa | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal › Code X1X.X9b | `empty`: nút không có nội dung và không có con |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › A Note on Factitious Illness and Malingering | `no_iasp_code`: no_iasp_code |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Guillain-Barre Syndrome | `no_iasp_code`: no_iasp_code |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Acute Herpes Zoster (Trigeminal) › Code 002.x2a | `empty`: nút không có nội dung và không có con |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Postherpetic Neuralgia (Trigeminal) › Code 003.X2b | `empty`: nút không có nội dung và không có con |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Geniculate Neuralgia (VIIth Cranial Nerve): Ramsay Hunt Syndrome › Code 006.X2 | `empty`: nút không có nội dung và không có con |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Post-traumatic Headache › Code 002.X l b | `empty`: nút không có nội dung và không có con |
| ⚠ | B. Relatively localized syndromes of the head and neck › Headache crosswalk | `unnumbered_chapter`: unnumbered_chapter |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Cervical Rib or Malformed First Thoracic Rib | `no_iasp_code`: no_iasp_code |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Tuberculosis of Larynx › Summary of Essential Features and Diagnostic | `empty`: nút không có nội dung và không có con |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to a Fracture | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to an Infection | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to a Neoplasm | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to Metabolic Bone Disease | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to Arthritis | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal Pain of Unknown or Uncertain Origin | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervico-Thoracic Spinal Pain of Unknown or Uncertain Origin › Code 13X.X8eS/C 23X.X8eR | `empty`: nút không có nội dung và không có con |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Trigger Point Syndrome | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to a Fracture | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to an Infection | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to a Neoplasm | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to Metabolic Bone Disease | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to Arthritis | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Pain Referred from Thoracic Viscera or Vessels and Perceived as Thoracic Spinal Pain | `no_iasp_code`: no_iasp_code |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal Pain of Unknown or Uncertain Origin | `no_iasp_code`: no_iasp_code |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Volkmann’s Ischemic Contracture › Code 222.X5 | `empty`: nút không có nội dung và không có con |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XVI: Pain of psychological origin in the lower limbs | `chapter_is_syndrome`: chapter_is_syndrome |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XVI: Pain of psychological origin in the lower limbs › Code | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XVI: Pain of psychological origin in the lower limbs › References | `orphan_section`: mục không thuộc bệnh nào |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Internal Mammary Artery Syndrome › Code 303.X1f | `empty`: nút không có nội dung và không có con |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Thoracic Visceral Disease with Pain Referred to Abdomen | `no_iasp_code`: no_iasp_code |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Colon › Code 452.X4 | `empty`: nút không có nội dung và không có con |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Porphyria—Hepatic Porphyrias | `no_code`: no_code |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Porphyria—Hepatic Porphyrias | `no_iasp_code`: no_iasp_code |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIII: Abdominal pain of psychological origin › Abdominal Pain—Visceral Pain Referred to the Abdomen | `no_code`: no_code |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIII: Abdominal pain of psychological origin › Abdominal Pain—Visceral Pain Referred to the Abdomen | `no_iasp_code`: no_iasp_code |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis | `missing_syndrome_title`: missing_syndrome_title |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Definition | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Main Features | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Diagnostic Criteria | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Treatment | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Code | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Reference | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Ovarian Pain › Code | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Neuralgia of Iliohypogastric, Ilio-inguinal, or Genito-Femoral Nerves | `empty`: nút không có nội dung và không có con |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Neuralgia of Iliohypogastric, Ilio-inguinal, or Genito-Femoral Nerves | `no_iasp_code`: no_iasp_code |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Testicular Pain | `no_code`: no_code |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Testicular Pain › Diagnostic Criteria | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Proctalgia Fugax › Code | `duplicate_path`: trùng tên mục với một mục khác cùng bệnh |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to a Fracture | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to an Infection | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to a Neoplasm | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to Metabolic Bone Disease | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to Arthritis | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Pain Referred From Abdominal Viscera or Vessels and Perceived as Lumbar Spinal Pain | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal Pain of Unknown or Uncertain Origin | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Upper Lumbar Spinal Pain of Unknown or Uncertain Origin › Code 5XX.X8cS | `empty`: nút không có nội dung và không có con |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbosacral Spinal Pain of Unknown or Uncertain Origin › Code 5XX.X8eS | `empty`: nút không có nội dung và không có con |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Trigger Point Syndrome | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Attributable to an Infection | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Attributable to a Neoplasm | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Attributable to Metabolic Bone Disease | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Attributable to Arthritis | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Pain Referred from Abdominal or Pelvic Viscera or Vessels Perceived as Sacral Spinal Pain | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Generalized Spinal Pain Attributable to Disseminated Neoplastic Disease | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Generalized Spinal Pain Attributable to Metabolic Bone Disease | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Generalized Spinal Pain Attributable to Arthritis | `no_iasp_code`: no_iasp_code |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Back Pain of Other Visceral or Neurological Origin Involving the Spine | `empty`: nút không có nội dung và không có con |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Back Pain of Other Visceral or Neurological Origin Involving the Spine | `no_iasp_code`: no_iasp_code |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Ischial Bursitis › Code 533.X3 | `empty`: nút không có nội dung và không có con |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Trochanteric Bursitis › Code 634.X3d | `empty`: nút không có nội dung và không có con |
| ℹ | Items usually provided in descriptions › Criteria | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | Items usually provided in descriptions › References | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Peripheral Neuropathy › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Peripheral Neuropathy › Complications | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Peripheral Neuropathy › Social and Physical Disabilities | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Stump Pain › Laboratory Findings | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Stump Pain › Essential Features | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Phantom Pain › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Phantom Pain › Main Features | dài 121 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) › Main Features | dài 137 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) › Associated Symptoms and Signs | dài 74 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) › Laboratory Findings | dài 81 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) › Usual Course | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type I (Reflex Sympathetic Dystrophy) › Diagnostic Criteria | dài 78 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type II (Causalgia) › Main Features | dài 155 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type II (Causalgia) › Laboratory Findings | dài 65 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type II (Causalgia) › Usual Course | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type II (Causalgia) › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Complex Regional Pain Syndrome, Type II (Causalgia) › Diagnostic Criteria | dài 73 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Central Pain › Site | dài 65 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Central Pain › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Central Pain › Main Features | dài 138 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Central Pain › Associated Symptoms and Signs | dài 98 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Central Pain › Pathology | dài 91 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Syndrome of Syringomyelia › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Syndrome of Syringomyelia › Main Features | dài 75 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Syndrome of Syringomyelia › Signs | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Syndrome of Syringomyelia › Pathology | dài 103 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Polymyalgia Rheumatica › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Polymyalgia Rheumatica › Aggravating Factors | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Polymyalgia Rheumatica › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Polymyalgia Rheumatica › Diagnostic Criteria | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Polymyalgia Rheumatica › Differential Diagnosis | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Main Features | dài 303 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Associated Symptoms and Signs | dài 102 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Etiology | dài 122 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Definition | dài 77 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Fibromyalgia (or Fibrositis) › Definition | dài 193 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Rheumatoid Arthritis › Main Features | dài 160 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Rheumatoid Arthritis › Diagnostic Criteria | dài 184 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteoarthritis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteoarthritis › Main Features | dài 159 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteoarthritis › Aggravating Features | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteoarthritis › Laboratory Findings | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Calcium Pyrophosphate Dihydrate Deposition Disease (CPPD) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Calcium Pyrophosphate Dihydrate Deposition Disease (CPPD) › Main Features | dài 121 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Calcium Pyrophosphate Dihydrate Deposition Disease (CPPD) › Complications | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Calcium Pyrophosphate Dihydrate Deposition Disease (CPPD) › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Gout › Main Features | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Gout › Diagnostic Criteria | dài 87 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Main Features | dài 218 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Associated Symptoms | dài 79 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Signs | dài 65 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Laboratory Findings | dài 100 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Usual Course | dài 107 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Relief | dài 147 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Social and Physical Disability | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › Pathology | dài 95 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Hemophilic Arthropathy › References | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Burns › Main Features | dài 279 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Burns › Pathology | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Burns › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Muscle Tension Pain › Main Features | dài 142 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Muscle Tension Pain › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Delusional or Hallucinatory › Main Features | dài 97 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal › Main Features | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal › Associated Symptoms | dài 480 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal › Essential Features | dài 165 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Hysterical, Conversion, or Hypochondriacal › Differential Diagnosis | dài 134 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Associated with Depression › Main Features | dài 115 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Associated with Depression › Differential Diagnosis | dài 69 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Pain of Psychological Origin: Associated with Depression › Code | dài 156 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Regional Sprains or Strains › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Sickle Cell Arthropathy › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Purpuric Arthropathy › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Stiff Man Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Paralysis Agitans › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Epilepsy › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Polyarteritis Nodosa › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Psoriatic Arthropathy and Other Secondary Arthropathies › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Painful Scar › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Systemic Lupus Erythematosis, Systemic Sclerosis and Fibrosclerosis, Polymyositis, and Dermatomyositis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Infective Arthropathies › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Traumatic Arthropathy › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteomyelitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteitis Deformans › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteochondritis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Osteoporosis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Muscle Spasm › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Local Pain, No Cause Specified › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Guillain-Barre Syndrome › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | A. Relatively generalized syndromes › GROUP I: Relatively generalized syndromes › Guillain-Barre Syndrome › Main Features | dài 88 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Trigeminal Neuralgia (Tic Douloureux) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Trigeminal Neuralgia (Tic Douloureux) › Main Features | dài 197 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Trigeminal Neuralgia (Tic Douloureux) › Differential Diagnosis | dài 70 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Trigeminal Neuralgia (Tic Douloureux) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Secondary Neuralgia (Trigeminal) from Central Nervous System Lesions › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Secondary Neuralgia (Trigeminal) from Central Nervous System Lesions › Main Features | dài 76 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Secondary Neuralgia (Trigeminal) from Central Nervous System Lesions › Differential Diagnosis | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Secondary Trigeminal Neuralgia from Facial Trauma › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Secondary Trigeminal Neuralgia from Facial Trauma › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Secondary Trigeminal Neuralgia from Facial Trauma › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Secondary Trigeminal Neuralgia from Facial Trauma › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Acute Herpes Zoster (Trigeminal) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Postherpetic Neuralgia (Trigeminal) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Postherpetic Neuralgia (Trigeminal) › Main Features | dài 70 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Postherpetic Neuralgia (Trigeminal) › Associated Symptoms | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Postherpetic Neuralgia (Trigeminal) › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Geniculate Neuralgia (VIIth Cranial Nerve): Ramsay Hunt Syndrome › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Nervus Intermedius › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Nervus Intermedius › Main Features | dài 104 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Nervus Intermedius › Associated Signs and Symptoms | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Nervus Intermedius › Complications | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Nervus Intermedius › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Glossopharyngeal Neuralgia (IXth Cranial Nerve) › Main Features | dài 95 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Glossopharyngeal Neuralgia (IXth Cranial Nerve) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Superior Laryngeal Nerve (Vagus Nerve Neuralgia) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Superior Laryngeal Nerve (Vagus Nerve Neuralgia) › Laboratory Findings | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Superior Laryngeal Nerve (Vagus Nerve Neuralgia) › Complications | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Neuralgia of the Superior Laryngeal Nerve (Vagus Nerve Neuralgia) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Occipital Neuralgia › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Occipital Neuralgia › Main Features | dài 74 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Occipital Neuralgia › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Hypoglossal Neuralgia › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Glossopharyngeal Pain from Trauma › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Hypoglossal Pain from Trauma › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Tolosa-Hunt Syndrome (Painful Ophthalmoplegia) › Main Features | dài 83 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Tolosa-Hunt Syndrome (Painful Ophthalmoplegia) › Precipitating Factors | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Tolosa-Hunt Syndrome (Painful Ophthalmoplegia) › Relief | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Tolosa-Hunt Syndrome (Painful Ophthalmoplegia) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Tolosa-Hunt Syndrome (Painful Ophthalmoplegia) › References | dài 105 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing) › Definition | dài 67 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing) › Main Features | dài 135 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing) › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › SUNCT Syndrome (Shortlasting, Unilateral Neuralgiform Pain with Conjunctival Injection and Tearing) › References | dài 87 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Raeder’s Syndrome (Raeder’s Paratrigeminal Syndrome) › Definition | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Raeder’s Syndrome (Raeder’s Paratrigeminal Syndrome) › Main Features | dài 244 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Raeder’s Syndrome (Raeder’s Paratrigeminal Syndrome) › Associated Symptoms and Signs | dài 80 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP II: Neuralgias of the head and face › Raeder’s Syndrome (Raeder’s Paratrigeminal Syndrome) › Duration and Usual Course | dài 75 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Acute Tension Headache › Main Features | dài 84 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Acute Tension Headache › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) › Definition | dài 90 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) › Main Features | dài 143 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) › Relief | dài 85 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) › Differential Diagnosis | dài 152 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Tension Headache: Chronic Form (Scalp Muscle Contraction Headache) › References | dài 99 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Temporomandibular Pain and Dysfunction Syndrome › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Temporomandibular Pain and Dysfunction Syndrome › Main Features | dài 155 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Temporomandibular Pain and Dysfunction Syndrome › Usual Course | dài 79 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Temporomandibular Pain and Dysfunction Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Temporomandibular Pain and Dysfunction Syndrome › References | dài 109 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Osteoarthritis of the Temporomandibular Joint › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Rheumatoid Arthritis of the Temporomandibular Joint › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Rheumatoid Arthritis of the Temporomandibular Joint › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Dystonic Disorders, Facial Dyskinesia › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP III: Craniofacial pain of musculoskeletal origin › Crushing Injury of Head or Face › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Maxillary Sinusitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Maxillary Sinusitis › Main Features | dài 150 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Maxillary Sinusitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 1. Due to Dentino-Enamel Defects › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 1. Due to Dentino-Enamel Defects › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 1. Due to Dentino-Enamel Defects › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 2. Pulpitis › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 2. Pulpitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 2. Pulpitis › Main Features | dài 80 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 2. Pulpitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 3. Periapical Periodontitis and Abscess › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 3. Periapical Periodontitis and Abscess › System | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 3. Periapical Periodontitis and Abscess › Differential Diagnosis | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 3. Periapical Periodontitis and Abscess › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 4. Tooth Pain Not Associated with Lesions (Atypical Odontalgia) › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 4. Tooth Pain Not Associated with Lesions (Atypical Odontalgia) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 4. Tooth Pain Not Associated with Lesions (Atypical Odontalgia) › Main Features | dài 69 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Odontalgia: Toothache 4. Tooth Pain Not Associated with Lesions (Atypical Odontalgia) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Glossodynia and Sore Mouth › Main Features | dài 103 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Glossodynia and Sore Mouth › Associated Symptoms | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Glossodynia and Sore Mouth › Signs and Laboratory Findings | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Glossodynia and Sore Mouth › Complications | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Cracked Tooth Syndrome › Site | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Cracked Tooth Syndrome › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Cracked Tooth Syndrome › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Cracked Tooth Syndrome › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Dry Socket › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Dry Socket › Main Features | dài 161 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Dry Socket › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Gingival Disease, Inflammatory › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Toothache, Cause Unknown › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Diseases of the Jaw, Inflammatory Conditions › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Other and Unspecified Pain in Jaws › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP IV: Lesions of the ear, nose, and oral cavity › Frostbite of Face › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Classic Migraine (Migraine with Aura) › Main Features | dài 420 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Classic Migraine (Migraine with Aura) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Common Migraine (Migraine without Aura) › Main Features | dài 87 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Common Migraine (Migraine without Aura) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Carotidynia › Main Features | dài 112 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Carotidynia › Relief | dài 70 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Carotidynia › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Mixed Headache › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Cluster Headache › Main Features | dài 185 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Cluster Headache › Associated Symptoms and Signs | dài 98 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety) › Main Features | dài 182 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety) › Associated Symptoms and Signs | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety) › Usual Course | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety) › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Chronic Paroxysmal Hemicrania (CPH) (Unremitting Form or Variety) › References | dài 88 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Chronic Paroxysmal Hemicrania (CPH) (Remitting Form or Variety) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Chronic Cluster Headache › Main Features | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Cluster-Tic Syndrome › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Cluster-Tic Syndrome › Main Features | dài 171 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Cluster-Tic Syndrome › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Cluster-Tic Syndrome › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Cluster-Tic Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Post-traumatic Headache › Site | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Post-traumatic Headache › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Post-traumatic Headache › Differential Diagnosis | dài 89 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › The Syndrome of “Jabs and Jolts” › Site | dài 69 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › The Syndrome of “Jabs and Jolts” › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › The Syndrome of “Jabs and Jolts” › Main Features | dài 286 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › The Syndrome of “Jabs and Jolts” › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Temporal Arteritis (Giant Cell Arteritis) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Temporal Arteritis (Giant Cell Arteritis) › Main Features | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Temporal Arteritis (Giant Cell Arteritis) › Laboratory Findings | dài 111 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Temporal Arteritis (Giant Cell Arteritis) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Headache Associated with Low CSF Pressure › Main Features | dài 98 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Headache Associated with Low CSF Pressure › Complications | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Headache Associated with Low CSF Pressure › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Post-Dural Puncture Headache › Main Features | dài 98 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Hemicrania Continua › System | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Hemicrania Continua › Main Features | dài 154 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Hemicrania Continua › Social and Physical Disability | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Hemicrania Continua › Differential Diagnosis | dài 67 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP V: Rimary headache syndromes, vascular disorders, and cerebrospinal fluid syndromes › Hemicrania Continua › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Stylohyoid Process Syndrome (Eagle’s Syndrome) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Stylohyoid Process Syndrome (Eagle’s Syndrome) › Radiologic Findings | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Stylohyoid Process Syndrome (Eagle’s Syndrome) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Cervicogenic Headache › Definition | dài 81 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Cervicogenic Headache › Site | dài 86 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Cervicogenic Headache › Main Features | dài 136 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Cervicogenic Headache › Tests and Laboratory Findings | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Cervicogenic Headache › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Cervicogenic Headache › References | dài 74 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Superior Pulmonary Sulcus Syndrome (Pancoast Tumor) › Definition | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Superior Pulmonary Sulcus Syndrome (Pancoast Tumor) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Superior Pulmonary Sulcus Syndrome (Pancoast Tumor) › Main Features | dài 101 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Superior Pulmonary Sulcus Syndrome (Pancoast Tumor) › Summary of Essential Features and Diagnostic Criteria | dài 70 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Superior Pulmonary Sulcus Syndrome (Pancoast Tumor) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Thoracic Outlet Syndrome › System Involved | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Thoracic Outlet Syndrome › Main Features | dài 160 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Thoracic Outlet Syndrome › Associated Symptoms | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Thoracic Outlet Syndrome › Signs and Laboratory Findings | dài 177 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Thoracic Outlet Syndrome › Summary of Essential Features and Diagnostic Criteria | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Thoracic Outlet Syndrome › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Pain of Skeletal Metastatic Disease of the Neck, Arm, or Shoulder Girdle › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Pain of Skeletal Metastatic Disease of the Neck, Arm, or Shoulder Girdle › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Pain of Skeletal Metastatic Disease of the Neck, Arm, or Shoulder Girdle › Main Feature | dài 79 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VII: Suboccipital and cervical musculoskeletal disorders › Pain of Skeletal Metastatic Disease of the Neck, Arm, or Shoulder Girdle › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Carcinoma of Thyroid › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Carcinoma of Thyroid › Complications | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Carcinoma of Thyroid › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Carcinoma of Larynx › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Carcinoma of Larynx › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Tuberculosis of Larynx › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Tuberculosis of Larynx › Differential Diagnosis | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Tuberculosis of Larynx › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | B. Relatively localized syndromes of the head and neck › GROUP VIII: Visceral pain in the neck › Carcinoma of Pharynx › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to a Fracture › Schedule of Fractures | dài 112 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to an Infection › Schedule of Sites of Infection | dài 123 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to a Neoplasm › Schedule of Neoplastic Diseases | dài 150 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Attributable to Arthritis › Remarks | dài 119 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly › Remarks | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Spinal Pain of Unknown or Uncertain Origin › Remarks | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Upper Cervical Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Lower Cervical Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Lower Cervical Spinal Pain of Unknown or Uncertain Origin › Remarks | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Lower Cervical Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Acceleration-Deceleration Injury of the Neck (Cervical Sprain) › Clinical Features | dài 111 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Acceleration-Deceleration Injury of the Neck (Cervical Sprain) › Remarks | dài 120 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Acceleration-Deceleration Injury of the Neck (Cervical Sprain) › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Torticollis (Spasmodic Torticollis) › Pathology | dài 164 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Discogenic Pain › Diagnostic Criteria | dài 152 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Discogenic Pain › Remarks | dài 78 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Discogenic Pain › References | dài 103 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Zygapophysial Joint Pain › Diagnostic Criteria | dài 269 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Zygapophysial Joint Pain › Pathology | dài 106 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Zygapophysial Joint Pain › References | dài 190 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Muscle Sprain › Diagnostic Criteria | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Muscle Sprain › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Trigger Point Syndrome › Diagnostic Criteria | dài 85 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Trigger Point Syndrome › Remarks | dài 134 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Alar Ligament Sprain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Segmental Dysfunction › Remarks | dài 128 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Cervical Segmental Dysfunction › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Radicular Pain Attributable to a Prolapsed Cervical Disk › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP IX: Cervical or radicular spinal pain syndromes › Traumatic Avulsion of Nerve Roots › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to an Infection › Schedule of Sites of Infection | dài 103 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to a Neoplasm › Schedule of Neoplastic Diseases | dài 148 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Attributable to Arthritis › Remarks | dài 90 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly › Remarks | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Spinal Pain of Unknown or Uncertain Origin › Remarks | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Upper Thoracic Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Upper Thoracic Spinal Pain of Unknown or Uncertain Origin › Remarks | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Upper Thoracic Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Midthoracic Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Lower Thoracic Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Lower Thoracic Spinal Pain of Unknown or Uncertain Origin › Remarks | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Lower Thoracic Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracolumbar Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracolumbar Spinal Pain of Unknown or Uncertain Origin › Remarks | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracolumbar Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Discogenic Pain › Diagnostic Criteria | dài 153 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Discogenic Pain › Remarks | dài 133 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Zygapophysial Joint Pain › Diagnostic Criteria | dài 269 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Zygapophysial Joint Pain › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Costo-Transverse Joint Pain › Diagnostic Criteria | dài 305 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Costo-Transverse Joint Pain › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Muscle Sprain › Diagnostic Criteria | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Trigger Point Syndrome › Diagnostic Criteria | dài 85 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Muscle Spasm › Diagnostic Features | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Muscle Spasm › Remarks | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Muscle Spasm › References | dài 111 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | D. Spinal pain, section 2: spinal and radicular pain syndromes of the cervical and thoracic regions › GROUP X: Thoracic spinal or radicular pain syndromes › Thoracic Segmental Dysfunction › Remarks | dài 135 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Tumors of the Brachial Plexus › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Tumors of the Brachial Plexus › Main Features | dài 69 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Tumors of the Brachial Plexus › Signs and Laboratory Findings | dài 65 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Tumors of the Brachial Plexus › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Chemical Irritation of the Brachial Plexus › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Chemical Irritation of the Brachial Plexus › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Chemical Irritation of the Brachial Plexus › Main Features | dài 88 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Chemical Irritation of the Brachial Plexus › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Traumatic Avulsion of the Brachial Plexus › Main Features | dài 297 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Traumatic Avulsion of the Brachial Plexus › Associated Symptoms | dài 123 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Traumatic Avulsion of the Brachial Plexus › Signs | dài 139 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Traumatic Avulsion of the Brachial Plexus › Summary of Essential Features and Diagnostic Criteria | dài 133 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Traumatic Avulsion of the Brachial Plexus › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Postradiation Pain of the Brachial Plexus › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Painful Arms and Moving Fingers › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Brachial Neuritis (Brachial Neuropathy, Neuralgic Amyotrophy, Parsonage-Turner Syndrome) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Bicipital Tendinitis › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Bicipital Tendinitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Bicipital Tendinitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Subacromial Bursitis (Subdeltoid Bursitis, Supraspinatus Tendinitis) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Subacromial Bursitis (Subdeltoid Bursitis, Supraspinatus Tendinitis) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Rotator Cuff Tear—Partial or Complete › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Rotator Cuff Tear—Partial or Complete › Complications | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Rotator Cuff Tear—Partial or Complete › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Lateral Epicondylitis (Tennis Elbow) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Lateral Epicondylitis (Tennis Elbow) › Aggravating Factors | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Lateral Epicondylitis (Tennis Elbow) › Laboratory and Radiologic Findings | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Lateral Epicondylitis (Tennis Elbow) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Medial Epicondylitis (Golfer’s Elbow) › Laboratory and Radiologic Findings | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Medial Epicondylitis (Golfer’s Elbow) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › DeQuervain’s Tenosynovitis › Site | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › DeQuervain’s Tenosynovitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › DeQuervain’s Tenosynovitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Osteoarthritis of the Hands › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Osteoarthritis of the Hands › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Cubital Tunnel Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Carpal Tunnel Syndrome › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Carpal Tunnel Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XI: Pain in the shoulder, arm, and hand › Crush Injury of Upper Limbs › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Raynaud’s Disease › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Raynaud’s Disease › Main Features | dài 169 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Raynaud’s Disease › Associated Symptoms and Signs | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Raynaud’s Disease › Differential Diagnosis | dài 130 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Frostbite and Cold Injury › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Frostbite and Cold Injury › Main Features | dài 142 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Frostbite and Cold Injury › Signs and Usual Course | dài 76 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Frostbite and Cold Injury › Pathology | dài 109 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Erythema Pernio (Chilblains) › Main Features | dài 75 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Acrocyanosis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XII: Vascular disease of the limbs › Livedo Reticularis › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIII: Collagen disease of the limbs › Scleroderma › Main Features | dài 70 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIII: Collagen disease of the limbs › Scleroderma › Associated Symptoms and Signs | dài 85 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIII: Collagen disease of the limbs › Ergotism › Main Features | dài 137 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIV: Vasodilating functional disease of the limbs › Erythromelalgia › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIV: Vasodilating functional disease of the limbs › Erythromelalgia › Main Features | dài 74 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIV: Vasodilating functional disease of the limbs › Thromboangiitis Obliterans › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIV: Vasodilating functional disease of the limbs › Thromboangiitis Obliterans › Main Features | dài 87 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIV: Vasodilating functional disease of the limbs › Thromboangiitis Obliterans › Signs | dài 88 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XIV: Vasodilating functional disease of the limbs › Chronic Venous Insufficiency › Associated Symptoms | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XV: Arterial insufficiency in the limbs › Intermittent Claudication (XV-1) and Rest Pain › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XV: Arterial insufficiency in the limbs › Intermittent Claudication (XV-1) and Rest Pain › Main Features | dài 80 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XV: Arterial insufficiency in the limbs › Intermittent Claudication (XV-1) and Rest Pain › Complications | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | E. Local syndromes of the upper limbs and relatively generalized syndromes of the upper and lower limbs › GROUP XV: Arterial insufficiency in the limbs › Intermittent Claudication (XV-1) and Rest Pain › Etiology | dài 125 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Acute Herpes Zoster › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Postinfectious and Segmental Peripheral Neuralgia › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Angina Pectoris › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Angina Pectoris › Signs and Laboratory Findings | dài 69 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Myocardial Infarction › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Pericarditis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Pericarditis › Signs and Laboratory Findings | dài 73 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Aneurysm of the Aorta › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Aneurysm of the Aorta › Pathology | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Aneurysm of the Aorta › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Diseases of the Diaphragm › Site | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Diseases of the Diaphragm › Signs and Laboratory Findings | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Carcinoma of Esophagus › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Carcinoma of Esophagus › Main Features | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Carcinoma of Esophagus › Differential Diagnosis | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Carcinoma of Esophagus › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Slipping Rib Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Postmastectomy Pain Syndrome: Chronic Nonmalignant › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Postmastectomy Pain Syndrome: Chronic Nonmalignant › Pathology | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Postmastectomy Pain Syndrome: Chronic Nonmalignant › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Late Postmastectomy Pain or Regional Carcinoma › Main Features | dài 69 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Late Postmastectomy Pain or Regional Carcinoma › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Post-thoracotomy Pain Syndrome › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Post-thoracotomy Pain Syndrome › Signs and Laboratory Findings | dài 83 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Internal Mammary Artery Syndrome › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Internal Mammary Artery Syndrome › Signs and Laboratory Findings | dài 80 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Tietze’s Syndrome— Costo-Chondritis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Fractured Ribs or Sternum › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Xiphoidalgia Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVII: Visceral and other chest pain › Carcinoma of the Lung or Pleura › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVIII: Chest pain of psychological origin › Muscle Tension Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVIII: Chest pain of psychological origin › Delusional Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVIII: Chest pain of psychological origin › Conversion Pain › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XVIII: Chest pain of psychological origin › With Depression › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Subphrenic Abscess › System | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Subphrenic Abscess › Signs and Laboratory Findings | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Herniated Abdominal Organs › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Esophageal Motility Disorders › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Esophageal Motility Disorders › Main Features | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Esophageal Motility Disorders › Associated Symptoms | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Esophageal Motility Disorders › Signs and Laboratory Findings | dài 137 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Esophageal Motility Disorders › Usual Course | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Esophageal Motility Disorders › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Reflux Esophagitis with Peptic Ulceration › Main Features | dài 78 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Reflux Esophagitis with Peptic Ulceration › Associated Symptoms | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Reflux Esophagitis with Peptic Ulceration › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Gastric Ulcer with Chest Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XIX: Chest pain referred from abdomen or gastrointestinal tract › Duodenal Ulcer with Chest Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Acute Herpes Zoster › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Postherpetic Neuralgia › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Twelfth Rib Syndrome › Main Features | dài 122 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Twelfth Rib Syndrome › Usual Course | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Twelfth Rib Syndrome › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Twelfth Rib Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Abdominal Cutaneous Nerve Entrapment Syndrome › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Abdominal Cutaneous Nerve Entrapment Syndrome › Main Features | dài 160 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XX: Abdominal pain of neurological origin › Abdominal Cutaneous Nerve Entrapment Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Cardiac Failure › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Gallbladder Disease › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Post-cholecystectomy Syndrome › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Post-cholecystectomy Syndrome › Usual Course | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Post-cholecystectomy Syndrome › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Gastric Ulcer › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Gastric Ulcer › Main Features | dài 80 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Gastric Ulcer › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Duodenal Ulcer › System | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Duodenal Ulcer › Main Features | dài 65 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Duodenal Ulcer › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Stomach › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Stomach › Associated Symptoms | dài 65 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Stomach › Signs and Laboratory Findings | dài 83 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Stomach › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Pancreas › Signs and Laboratory Findings | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Pancreas › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Mesenteric Ischemia › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Mesenteric Ischemia › Signs and Laboratory Findings | dài 79 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Mesenteric Ischemia › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Crohn's Disease › Complications | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Crohn's Disease › Etiology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Constipation › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Constipation › Main Features | dài 83 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Constipation › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Irritable Bowel Syndrome › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Irritable Bowel Syndrome › Main Features | dài 81 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Irritable Bowel Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Diverticular Disease of the Colon › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Diverticular Disease of the Colon › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Colon › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Colon › Main Features | dài 90 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Gastritis and Duodenitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Dyspepsia and Other Dysfunctional Disorders in Stomach with Pain › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Radiation Enterocolitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Ulcerative Colitis and Other Chronic Colitis and Other Ulcer › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Post-Gastric Surgery Syndrome, Dumping › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Chronic Pancreatitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Recurrent Abdominal Pain in Children › Site | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Recurrent Abdominal Pain in Children › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Recurrent Abdominal Pain in Children › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Recurrent Abdominal Pain in Children › References | dài 74 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Liver or Biliary System › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXI: Abdominal pain of visceral origin › Carcinoma of the Kidney (Grawitz Carcinoma) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Familial Mediterranean Fever (FMF) › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Familial Mediterranean Fever (FMF) › Main Features | dài 98 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Familial Mediterranean Fever (FMF) › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Familial Mediterranean Fever (FMF) › Treatment | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Familial Mediterranean Fever (FMF) › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Abdominal Migraine › Site | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Abdominal Migraine › Main Features | dài 108 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Abdominal Migraine › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Abdominal Migraine › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Abdominal Migraine › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Intermittent Acute Porphyria (IAP) › Main Features | dài 97 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Intermittent Acute Porphyria (IAP) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Hereditary Coproporphyria (HCP) › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Hereditary Coproporphyria (HCP) › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Hereditary Coproporphyria (HCP) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Variegate Porphyria (VP) › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Variegate Porphyria (VP) › Main Features | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Variegate Porphyria (VP) › Signs | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXII: Abdominal pain syndromes of generalized diseases › Variegate Porphyria (VP) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIII: Abdominal pain of psychological origin › Muscle Tension Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIII: Abdominal pain of psychological origin › Delusional or Hallucinatory Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIII: Abdominal pain of psychological origin › Conversion Pain › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIII: Abdominal pain of psychological origin › Associated with Depression › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Mittelschmerz › Main Features | dài 137 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Mittelschmerz › Diagnostic Criteria and Differential Diagnosis | dài 107 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Mittelschmerz › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Secondary Dysmenorrhea › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Secondary Dysmenorrhea › Main Causes | dài 1023 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Primary Dysmenorrhea › Main Features | dài 190 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Primary Dysmenorrhea › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Primary Dysmenorrhea › Pathophysiology | dài 147 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Primary Dysmenorrhea › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Endometriosis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Endometriosis › Main Features | dài 265 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Endometriosis › Usual Course | dài 99 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Endometriosis › Diagnostic Criteria | dài 95 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Endometriosis › Treatment | dài 115 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Endometriosis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Posterior Parametritis › Main Features | dài 85 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Posterior Parametritis › Diagnostic Criteria and Treatment | dài 89 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Posterior Parametritis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Main Features | dài 118 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Diagnostic Criteria | dài 79 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Main Features | dài 103 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Diagnostic Criteria | dài 170 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Treatment | dài 123 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Tuberculous Salpingitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Ovarian Pain › Definition | dài 135 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Ovarian Pain › Code | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Ovarian Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › Main Features | dài 136 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › Associated Symptoms | dài 160 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › Pathology | dài 388 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › Treatment | dài 187 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › Code 763.X8 | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Chronic Pelvic Pain Without Obvious Pathology (CPPWOP) › References | dài 114 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Pain from Urinary Tract › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Pain of Vaginismus or Dyspareunia › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXIV: Diseases of the bladder, uterus, ovaries, and adnexa › Carcinoma of the Bladder › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Testicular Pain › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Testicular Pain › Main Features | dài 160 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Testicular Pain › Signs | dài 186 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Proctalgia Fugax › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Proctalgia Fugax › References | dài 116 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Proctalgia Fugax › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Ulcer of Anus or Rectum › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Injury of External Genitalia › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | F. Visceral and other syndromes of the trunk apart from spinal and radicular pain › GROUP XXV: Pain in the rectum, perineum, and external genitalia › Carcinoma of the Prostate › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to an Infection › Schedule of Sites of Infection | dài 104 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to a Neoplasm › Schedule of Neoplastic Diseases | dài 141 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Attributable to Arthritis › Remarks | dài 107 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Pseudarthrosis of a Transitional Vertebra › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal Pain of Unknown or Uncertain Origin › Remarks | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Upper Lumbar Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Upper Lumbar Spinal Pain of Unknown or Uncertain Origin › Remarks | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lower Lumbar Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lower Lumbar Spinal Pain of Unknown or Uncertain Origin › Remarks | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lower Lumbar Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbosacral Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbosacral Spinal Pain of Unknown or Uncertain Origin › Remarks | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain after Failed Spinal Surgery › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain after Failed Spinal Surgery › Remarks | dài 134 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Spinal or Radicular Pain after Failed Spinal Surgery › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Discogenic Pain › Diagnostic Criteria | dài 153 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Discogenic Pain › Remarks | dài 78 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Discogenic Pain › References | dài 96 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Internal Disk Disruption › Pathology | dài 149 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Internal Disk Disruption › References | dài 76 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Zygapophysial Joint Pain › Diagnostic Criteria | dài 268 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Zygapophysial Joint Pain › Pathology | dài 106 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Zygapophysial Joint Pain › References | dài 247 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Muscle Sprain › Diagnostic Criteria | dài 71 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Muscle Sprain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Muscle Sprain › References | dài 116 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Trigger Point Syndrome › Diagnostic Criteria | dài 83 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Muscle Spasm › Remarks | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Muscle Spasm › References | dài 116 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Segmental Dysfunction › Remarks | dài 157 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Segmental Dysfunction › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Ligament Sprain › Diagnostic Criteria | dài 115 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Ligament Sprain › Remarks | dài 106 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Ligament Sprain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Sprain of the Anulus Fibrosus › Pathology | dài 98 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Sprain of the Anulus Fibrosus › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Interspinous Pseudarthrosis (Kissing Spines, Baastrup’s Disease) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Instability › Remarks | dài 103 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Instability › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Lumbar Instability › References | dài 134 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Spondylolysis › Remarks | dài 86 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVI: Lumbar or radicular spinal pain syndromes › Spondylolysis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Attributable to a Fracture › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Attributable to an Infection › Schedule of Sites of Infection | dài 66 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Attributable to a Neoplasm › Schedule of Neoplastic Diseases | dài 108 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Spinal Stenosis: Cauda Equina Lesion › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Spinal Stenosis: Cauda Equina Lesion › Main Features | dài 103 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Spinal Stenosis: Cauda Equina Lesion › Aggravating Factors | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Spinal Stenosis: Cauda Equina Lesion › Signs and Laboratory Findings | dài 74 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Spinal Stenosis: Cauda Equina Lesion › Pathology | dài 220 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Spinal Stenosis: Cauda Equina Lesion › Treatment | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal or Radicular Pain Associated with a Congenital Vertebral Anomaly › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal Pain of Unknown or Uncertain Origin › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal Pain of Unknown or Uncertain Origin › Remarks | dài 113 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacral Spinal Pain of Unknown or Uncertain Origin › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacroiliac Joint Pain › Remarks | dài 137 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVII: Sacral spinal or radicular pain syndromes › Sacroiliac Joint Pain › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVIII: Coccygeal pain syndromes › Coccygeal Pain of Unknown or Uncertain Origin › Pathology | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVIII: Coccygeal pain syndromes › Coccygeal Pain of Unknown or Uncertain Origin › Remarks | dài 114 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXVIII: Coccygeal pain syndromes › Coccygeal Pain of Unknown or Uncertain Origin › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Generalized Spinal Pain Attributable to Multiple Fractures › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Ankylosing Spondylitis › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Ankylosing Spondylitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Ankylosing Spondylitis › Main Features | dài 84 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Ankylosing Spondylitis › Aggravating Features | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Ankylosing Spondylitis › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Tumor Infiltration of the Lumbosacral Plexus › Main Features | dài 92 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Tumor Infiltration of the Lumbosacral Plexus › Signs and Laboratory Findings | dài 110 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Tumor Infiltration of the Lumbosacral Plexus › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Tumor Infiltration of the Sacrum and Sacral Nerves › Main Features | dài 72 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | G. Spinal pain, section 3: spinal and radicular pain syndromes of the lumbar, sacral, and coccygeal regions › GROUP XXIX: Diffuse or generalized spinal pain › Tumor Infiltration of the Sacrum and Sacral Nerves › Signs and Laboratory Findings | dài 80 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica) › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica) › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica) › Main Features | dài 68 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica) › Relief | dài 67 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Lateral Femoral Cutaneous Neuropathy (Meralgia Paresthetica) › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Obturator Neuralgia › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Femoral Neuralgia › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Sciatica Neuralgia › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Sciatica Neuralgia › Code | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Interdigital Neuralgia of the Foot (Morton’s Metatarsalgia) › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Interdigital Neuralgia of the Foot (Morton’s Metatarsalgia) › Laboratory Tests | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Interdigital Neuralgia of the Foot (Morton’s Metatarsalgia) › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Injection Neuropathy › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Gluteal Syndromes › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Gluteal Syndromes › Main Features | dài 183 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Gluteal Syndromes › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Piriformis Syndrome › Main Features | dài 114 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Piriformis Syndrome › Signs | dài 106 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Piriformis Syndrome › Relief | dài 124 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Piriformis Syndrome › Pathology | dài 153 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Piriformis Syndrome › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Piriformis Syndrome › References | dài 195 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Painful Legs and Moving Toes › Main Features | dài 127 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Painful Legs and Moving Toes › Usual Course | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Painful Legs and Moving Toes › References | dài 67 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Metastatic Disease › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Peroneal Muscular Atrophy (Charcot-Marie-Tooth Disease) › System | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Peroneal Muscular Atrophy (Charcot-Marie-Tooth Disease) › Main Features | dài 149 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXI: Local syndromes in the leg or foot: pain of neurological origin › Peroneal Muscular Atrophy (Charcot-Marie-Tooth Disease) › Usual Course | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Ischial Bursitis › Site | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Ischial Bursitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Ischial Bursitis › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Trochanteric Bursitis › Site | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Trochanteric Bursitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Trochanteric Bursitis › Main Features | dài 78 từ (> 4 × trung vị 16) - có thể nuốt tiêu đề kế tiếp |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Trochanteric Bursitis › Complications | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXII: Pain syndromes of the hip and thigh of musculoskeletal origin › Osteoarthritis of the Hip › Code | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Spinal Stenosis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Osteoarthritis of the Knee › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Osteoarthritis of the Knee › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Night Cramps › Site | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Night Cramps › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Night Cramps › Differential Diagnosis | ngắn 3 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Night Cramps › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Plantar Fasciitis › Site | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Plantar Fasciitis › System | ngắn 2 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ℹ | H. Local syndromes of the lower limbs › GROUP XXXIII: Musculoskeletal syndromes of the leg › Plantar Fasciitis › Code | ngắn 1 từ (< 0.25 × trung vị 16) - kiểm tra có bị cắt không |
| ⚠ | (lần chạy) | cấp tiêu đề: Mục lục có 'List of Items Usually Provided in Detailed Descriptions of Pain Syndromes' nhưng không tìm thấy tiêu đề nào khớp trong thân sách. |
| ⚠ | (lần chạy) | cây: Mục lục 'List of Items Usually Provided in Detailed Descriptions of Pain Syndromes': 0 nút khớp trong cây (cần đúng 1). |
| ⚠ | (lần chạy) | cây: 'Definition' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Site' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'System(s)' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Main Features' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Associated Symptoms — aggravating and relieving agents' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Signs' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Laboratory Findings' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Usual Course' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Complications' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Social and Physical Disability' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Pathology' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Summary of Essential Features and Diagnostic Criteria' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Criteria' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Differential Diagnosis' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Code(s)' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'References' (trang PDF 54) không có nút cha đúng cấp - gắn tạm vào 'Items usually provided in descriptions'. |
| ⚠ | (lần chạy) | cây: 'Code' (trang PDF 152) không có nút cha đúng cấp - gắn tạm vào 'GROUP XVI: Pain of psychological origin in the lower limbs'. |
| ⚠ | (lần chạy) | cây: 'References' (trang PDF 152) không có nút cha đúng cấp - gắn tạm vào 'GROUP XVI: Pain of psychological origin in the lower limbs'. |
| ⚠ | (lần chạy) | thuộc tính: 'Tuberculous Salpingitis': mục Definition ở PDF 185 nằm sau mục Code/References - nghi sách thiếu tên một hội chứng (nội dung bị gộp vào đây). |
| ⚠ | (lần chạy) | thuộc tính: 5 hội chứng không có mã (L9): 'Complex Regional Pain Syndromes (CRPS)' (PDF 56); 'Note: Specific Myofascial Pain Syndromes' (PDF 63); 'Porphyria—Hepatic Porphyrias' (PDF 177); 'Abdominal Pain—Visceral Pain Referred to the Abdomen' (PDF 179); 'Testicular Pain' (PDF 188) |
| ⚠ | (lần chạy) | thuộc tính: 42 hội chứng không tìm thấy mã IASP 5 trục (mục Code). |

