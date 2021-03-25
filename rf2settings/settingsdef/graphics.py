adjustable_graphics_settings = {
    'Track Detail': {'name': 'Circuit Detail', 'value': 2,
                     'settings':
                         ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                          {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                     },
    'Player Detail': {'name': 'Player Detail', 'value': 3,
                      'settings':
                          ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                           {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                      },
    'Opponent Detail': {'name': 'Opponent Detail', 'value': 2,
                        'settings':
                            ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                             {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                        },
    'Texture Detail': {'name': 'Texture Detail', 'value': 3,
                       'settings':
                           ({'value': 0, 'name': 'Low'}, {'value': 1, 'name': 'Medium'},
                            {'value': 2, 'name': 'High'}, {'value': 3, 'name': 'Full'}),
                       },
    'Texture Filter': {'name': 'Texture Filter', 'value': 4,
                       'settings':
                           ({'value': 0, 'name': 'Bilinear'}, {'value': 1, 'name': 'Trilinear'},
                            {'value': 2, 'name': 'x2 Anisotropic'}, {'value': 3, 'name': 'x4 Anisotropic'},
                            {'value': 4, 'name': 'x8 Anisotropic'}, {'value': 5, 'name': 'x16 Anisotropic'}),
                       },
    'Special FX': {'name': 'Special Effects', 'value': 4,
                   'settings':
                       ({'value': 0, 'name': 'Off'},
                        {'value': 1, 'name': 'Low', 'perf': 'G+0,18% C+0,00%'},
                        {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'},
                        {'value': 4, 'name': 'Ultra', 'perf': 'G+0,90% C+2,20%'}),
                   },
    'Shadows': {'name': 'Shadows', 'value': 3,
                'settings':
                    ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low'},
                     {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'}, {'value': 4, 'name': 'Ultra'}),
                },
    'Shadow Blur': {'name': 'Shadow Blur', 'value': 2,
                    'settings':
                        ({'value': 0, 'name': 'Off'},
                         {'value': 1, 'name': 'Fast', 'perf': 'G+1,50% C+0,00%'},
                         {'value': 2, 'name': 'Optimal', 'perf': 'G+3,0% C+0,50%'},
                         {'value': 3, 'name': 'Quality', 'perf': 'G+8,5% C+1,00%'}),
                    },
    'Soft Particles': {'name': 'Soft Particles', 'value': 1,
                       'settings':
                            ({'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low', 'desc': 'Cheap soft edges'},
                             {'value': 2, 'name': 'High', 'desc': 'Depth buffered soft edges',
                              'perf': 'G+0,57% C+2,57%'}),
                       },
    'Rain FX Quality': {'name': 'Rain Drops', 'value': 3,
                        'settings':
                            ({'value': 1, 'name': 'Off', 'desc': 'Anything else than off will have a massive '
                                                                 'performance impact!'},
                             {'value': 2, 'name': 'Low', 'perf': 'G+4,10% C+6,30%'},
                             {'value': 3, 'name': 'Medium'}, {'value': 4, 'name': 'High'},
                             {'value': 5, 'name': 'Ultra', 'perf': 'G+17,2% C+6,70%'}),
                        },
    'Road Reflections': {'name': 'Road Reflection', 'value': 2,
                         'settings':
                            ({'value': 0, 'name': 'Off',
                              'desc': 'It will be hard to spot wet track areas! '
                                      'The Low setting is free on GPU but CPU heavy'},
                             {'value': 1, 'name': 'Low',
                              'desc': 'Reflected objects are generated '
                                      'for wet road and heat mirage',
                              'perf': 'G+0,33% C+5,39%'},
                             {'value': 2, 'name': 'High',
                              'desc': 'Reflected objects are generated for wet road and heat mirage'},
                             {'value': 3, 'name': 'Ultra',
                              'desc': 'Adds reflection blurring',
                              'perf': 'G+6,40% C+9,40%'}),
                         },
    'Environment Reflections': {'name': 'Environment Reflection', 'value': 2,
                                'settings':
                                    ({'value': 0, 'name': 'Off'},
                                     {'value': 1, 'name': 'Low',
                                      'desc': 'Live cubic mapping is used '
                                              '(if track and car are setup properly)'},
                                     {'value': 2, 'name': 'Medium',
                                      'desc': 'Live cubic mapping is used '
                                              '(if track and car are setup properly)'},
                                     {'value': 3, 'name': 'High',
                                      'desc': 'Live cubic mapping is used '
                                              '(if track and car are setup properly)'
                                      },
                                     {'value': 4, 'name': 'Ultra',
                                      'desc': 'v1124 RC: increase refresh rate and resolution'
                                      }
                                     ),
                                },
    'LSI Top': {'name': 'Low Speed Info', 'value': 0.15,
                'settings': ({'settingType': 'range', 'min': 0.01, 'max': 1.0, 'step': 0.01, 'display': 'floatpercent',
                              'desc': 'Vertical position of Low Speed Info message box as a fraction '
                                      'of screen height (-1 to disable)'},)
                },
    'Stabilize Horizon': {'name': 'Stabilize Horizon', 'value': 1,
                          'settings': (
                              {'value': 0, 'name': 'Off'}, {'value': 1, 'name': 'Low'},
                              {'value': 2, 'name': 'Medium'}, {'value': 3, 'name': 'High'}),
                          },
    'Steering Wheel': {'name': 'Steering Wheel', 'value': 0,
                       'settings': (
                           {'value': 0, 'name': 'On [Default]', 'desc': 'Moving steering wheel and arms'},
                           {'value': 1, 'name': 'Fixed', 'desc': 'Non-moving steering wheel or arms'},
                           {'value': 2, 'name': 'Off', 'desc': 'No steering wheel or arms (in cockpit only '
                                                               'while player-controlled)'},
                           {'value': 3, 'name': 'No arms', 'desc': 'Moving steering wheel but no arms'},
                       )},
    'Max Visible Vehicles': {'name': 'Visible Vehicles', 'value': 12,
                             'settings': ({'settingType': 'range', 'min': 5, 'max': 105, 'step': 1,
                                           'desc': 'rFactor 2 default setting: 12'},)},
}
advanced_settings = {
    'Transparency AA': {'name': 'Transparency AA', 'value': True,
                        'settings': ({'value': False, 'name': 'Disabled'},
                                     {'value': True, 'name': 'Enabled [Default]',
                                      'desc': 'Soften edges around alpha test objects'})
                        },
    'Texture Sharpening': {'name': 'Texture Sharpening', 'value': 5,
                           'settings': (
                              {'value': 0, 'name': 'Off', },
                              {'value': 1, 'name': '+2.0', 'desc': 'Sharpen textures using MIP LOD bias (very blurry)'},
                              {'value': 2, 'name': '+1.0', 'desc': 'Sharpen textures using MIP LOD bias (blurry)'},
                              {'value': 3, 'name': '-1.0', 'desc': 'Sharpen textures using MIP LOD bias (sharp)'},
                              {'value': 4, 'name': '-2.0', 'desc': 'Sharpen textures using MIP LOD bias (very sharp)'},
                              {'value': 5, 'name': 'Auto [Default]'},
                           ), },
    'Heat FX Fade Speed': {'name': 'Heat FX Fade Speed', 'value': 30,
                           'settings': ({'value': 30, 'name': '30 [Default]',
                                         'desc': 'Speed at which exhaust heat effects reduce '
                                                 'by half (0 to completely disable)'},
                                        {'value': 0, 'name': '0',
                                         'desc': 'Fixes visual artefact bubble behind certain cars in VR.'},
                                        )
                           },
    'Rearview Particles': {'name': 'Rearview Particles', 'value': True,
                           'settings': ({'value': False, 'name': 'Disabled'},
                                        {'value': True, 'name': 'Enabled [Default]', 'perf': 'G+3,30% C+1,44%',
                                         'desc': 'Show particles like rain spray in the rear view mirror'})
                           },
    'Rearview_Back_Clip': {'name': 'Rearview Back Clip', 'value': 0,
                           'settings': ({'settingType': 'range', 'min': 0, 'max': 250, 'step': 20,
                                         'desc': 'Back plane distance(view distance) for mirror '
                                                 '(0.0 = use default for scene)'}, )},
    'Rearview Driving': {'name': 'Rearview Driving', 'value': 1,
                         'settings': (
                             {'value': 0, 'name': 'Off', 'desc': 'Applies to in-game nosecam, '
                                                                 'cockpit, and TV cockpit'},
                             {'value': 1, 'name': 'Center+Sides'}, {'value': 2, 'name': 'Center'},
                             {'value': 3, 'name': 'Sides',
                              'desc': '(virtual mirrors only, in-car mirrors are on/off)'},
                         ), },
    'Rearview Onboard': {'name': 'Rearview Onboard', 'value': 0,
                         'settings': (
                             {'value': 0, 'name': 'Off', 'desc': 'Applies to in-game onboard cams'},
                             {'value': 1, 'name': 'Center+Sides'}, {'value': 2, 'name': 'Center'},
                             {'value': 3, 'name': 'Sides', 'desc': '(virtual mirrors only, in-car mirrors are on/off)'},
                         ), },
    'Rearview Swingman': {'name': 'Rearview Swingman', 'value': 0,
                          'settings': (
                             {'value': 0, 'name': 'Off', 'desc': 'Applies to in-game Swingman Cam'},
                             {'value': 1, 'name': 'Center+Sides'}, {'value': 2, 'name': 'Center'},
                             {'value': 3, 'name': 'Sides', 'desc': '(virtual mirrors only, in-car mirrors are on/off)'},
                         ), },
    'Screenshot Format': {'name': 'Screenshot Format', 'value': 0,
                          'settings': (
                              {'value': 0, 'name': 'default (jpg)'}, {'value': 1, 'name': 'bmp'},
                              {'value': 2, 'name': 'jpg'}, {'value': 3, 'name': 'png'}, {'value': 4, 'name': 'dds'},
                              {'value': 5, 'name': 'clipboard'},
                          ), },
    'Sun Occlusion': {'name': 'Sun Occlusion', 'value': False,
                      'settings': (
                          {'value': False, 'name': 'Off [Default]'},
                          {'value': True, 'name': 'On', 'desc': 'Sunlight is affected by cloud cover'},
                      ), },
    'Max Framerate': {'name': 'Max Framerate', 'value': 0,
                      'settings': ({'settingType': 'range', 'min': 0, 'max': 288, 'step': 1,
                                    'desc': '0 to disable, rFactor 2 default setting: 0'},)},
}
adjustable_video_settings = {
    'VrSettings': {'name': 'VR', 'value': 0, '_type': int,
                   'settings': ({'value': 0, 'name': 'Disabled'}, {'value': 1, 'name': 'HMD only'},
                                {'value': 2, 'name': 'HMD + Mirror'})
                   },
    'FSAA': {'name': 'Anti Aliasing (old)', 'value': 0, '_type': int,
             'settings': ({'value': 0, 'name': 'Off'},
                          {'value': 32, 'name': 'Level 1', 'desc': '2x [2x Multisampling]', 'perf': 'G+0,20% C+0,00%'},
                          {'value': 33, 'name': 'Level 2', 'desc': '2xQ [2x Quincunx (blurred)]',
                           'perf': 'G+8,20% C+1,45%'},
                          {'value': 34, 'name': 'Level 3', 'desc': '4x [4x Multisampling]', 'perf': 'G+14,62% C+0,17%'},
                          {'value': 35, 'name': 'Level 4', 'desc': '8x [8x CSAA (4 color + 4 cv samples)]',
                           'perf': 'G+1,1% C+0,95%'},
                          {'value': 36, 'name': 'Level 5', 'desc': '16x [16x CSAA (4 color + 12 cv samples)]',
                           'perf': 'G+0,0% C+0,0%'},
                          # {'value': 32, 'name': 'Level 6', 'desc': '8xQ [8x Multisampling]'},
                          # {'value': 32, 'name': 'Level 7', 'desc': '16xQ [16x CSAA (8 color + 8 cv samples)]'},
                          # {'value': 32, 'name': 'Level 8', 'desc': '32x [32x CSAA (8 color + 24 cv samples)]'},
                          )
             },
    'MSAA': {'name': 'Anti Aliasing', 'value': 0, '_type': int,
             'settings': ({'value': 0, 'name': 'Off'},
                          {'value': 2, 'name': '2x MSAA', 'desc': '2x [2x Multisampling]', 'perf': 'G+0,20% C+0,00%'},
                          {'value': 4, 'name': '4x MSAA', 'desc': '4x [4x Multisampling]', 'perf': 'G+14,62% C+0,17%'},
                          {'value': 8, 'name': '8x MSAA', 'desc': '8x [8x Multisampling]',
                           'perf': 'G+1,1% C+0,95%'}
                          )
             },
    'EPostProcessingSettings': {'name': 'Post Effects', 'value': 1, '_type': int,
                                'settings': ({'value': 1, 'name': 'Off',},
                                             {'value': 2, 'name': 'Low', 'desc': 'Glare Effects',
                                              'perf': 'G+0,5% C+0,59%'},
                                             {'value': 3, 'name': 'Medium', 'desc': 'Glare Effects and Depth of Field',
                                              'perf': 'G+9,0% C+5,0%'},
                                             {'value': 4, 'name': 'High', 'desc': 'All Effects at High Quality',
                                              'perf': 'G+15,0% C+5,0%'},
                                             {'value': 5, 'name': 'Ultra', 'desc': 'All Effects at Ultra Quality',
                                              'perf': 'G+25,0% C+5,0%'},
                                )},
    'UseFXAA': {'name': 'FXAA', 'value': 0, '_type': int, 'desc': 'Can not be used with FSAA. You should prefer FSAA '
                                                                  'whenever possible.',
                'settings': ({'value': 0, 'name': 'Off'},
                             {'value': 1, 'name': 'On', 'desc': 'Cheap post processing filter to smooth '
                                                                'high contrast edges.'})},
    }
resolution_video_settings = {
    'WindowedMode': {'name': 'Windowed Mode', 'value': None, 'hidden': True,
                     'settings': ({'value': 0, 'name': 'Fullscreen'}, {'value': 1, 'name': 'Windowed'})
                     },
    'Borderless': {'name': 'Borderless', 'value': None, 'hidden': True,
                   'settings': ({'value': 0, 'name': 'Windowed'}, {'value': 1, 'name': 'Borderless'})
                   },
    'VideoMode': {'name': 'Resolution', 'value': None, 'hidden': True,
                  'settings': ({'value': 125, 'name': 'FullHD'}, )
                  },
    'VideoRefresh': {'name': 'Refresh Rate', 'value': None, 'hidden': True,
                     'settings': ({'value': 1, 'name': '60Hz'}, )
                     },
    }
