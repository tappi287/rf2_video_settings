<template>
  <div v-cloak id="wiki" class="position-relative mb-5 text-left">
    <b-card class="setting-card" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">About</span></h6>
      </template>
      <a href="https://www.github.com/tappi287/rf2_video_settings" target="_blank" class="text-rf-orange">
        rf2 Settings Widget v{{ ver }}
      </a>
      published under MIT license &#169; 2020-2021
      <a href="https://sim-site.netlify.app" target="_blank" class="text-rf-orange">Stefan Tapper</a>
      <p class="mt-2">
        If you feel like it: <a href="https://sim-site.netlify.app/page/donate" target="_blank"
                                class="text-rf-orange">donate</a>.
      </p>
    </b-card>

    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">Wiki</span></h6>
      </template>
      <h6 class="mt-1">Pin to taskbar</h6>
      <p>If you want to pin this app to your taskbar: type rf2 into your Windows start menu and right click the
        rf2 Settings Widget app entry > Pin to taskbar. If you try to pin the running app, you'll pin
        a shortcut to your web browser.</p>

      <h6 class="mt-5">Report a bug</h6>
      <p>Want to report a bug, request a feature or have a setting you're missing? Head over to GitHub and
        <b-link class="text-rf-orange" target="_blank" href="https://github.com/tappi287/rf2_video_settings/issues">
          create an issue
        </b-link>.
      </p>

      <h6 class="mt-5">Import</h6>
      <p>You can import preset JSON files, exported from this app, by simply dragging them into the application window!
      This also works for rFactors player.JSON files. Simply drop it on the application and it will import all the
      settings available in this widget(and only those!).</p>
      <i>This is handy if you import someone else's player.JSON and want to make sure you are not overwriting all your
      other settings like your Player Name and Nickname.</i>

      <h6 class="mt-5">Server Browser</h6>
      <p>The Server Browser uses Steam's API to query server information. The number of connected players and
      names of the connected players does most likely not reflect the actual number of players.
      The information should be similar to what you see when launching Steam>View>Server</p>

      <h6 class="mt-5">rF2 Notes</h6>
      <p>Start rF2 while a dedicated server is running on the same machine: Change the WebUI Port in player.json
      to something different than the default value. Use this app to start rF2 or create a shortcut to rF2.exe
      and set the StartIn parameter to the rFactor 2 root directory.</p>
      <p></p>
      <span>Start rF2 from command line and join a password protected server: </span>
      <pre class="text-muted">rFactor2.exe +multiplayer +connect=:Password@IP:Port</pre>
      <p></p>
      <span>Server XY won't let you join: Unable to install server mod. Take a look at your:</span>
      <pre class="text-muted mb-0">rFactor 2\UserData\cmpReport.txt</pre>
      <span>If you find messages like component XY missing: try to un- and resubscribe to that Item in the
      Steam Workshop.</span>
      <p></p>
      <span>Your ModMgr.exe is not starting. The registry key for the packages and rFactor directory
      is most likely out of date. Take a look at these Windows registry keys:</span>
      <pre class="text-muted">HKEY_CURRENT_USER\\SOFTWARE\\Image Space Incorporated\\rFactor2 Mod Manager\\--guid--\\Packages Dir</pre>
    </b-card>

    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">Credits</span></h6>
      </template>
      <b-list-group class="low-round">
        <b-list-group-item class="bg-dark text-white">
          <b-link class="text-rf-orange" target="_blank" href="https://studio397.com">Studio 397 Dev Guide</b-link>
          <span> - general resource about rFactor 2 development</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link class="text-rf-orange" target="_blank" href="https://github.com/ChrisKnott/Eel">Eel</b-link>
          <span> - A little Python library for making simple Electron-like HTML/JS GUI apps</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link class="text-rf-orange" target="_blank" href="https://github.com/TonyWhitley/rF2_serverNotify">
            rF2_serverNotify
          </b-link>
          <span> - starting point to read rF2 Server information</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link class="text-rf-orange" target="_blank" href="https://gitlab.com/grumbel/rfactortools">
            rfactortools
          </b-link>
          <span> - interesting source of information to handle various rF specific file types.</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link class="text-rf-orange" target="_blank" href="https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/">
            Studio 397 Screenshot Thread
          </b-link>
          <span> - most of the dashboard shots are taken from there, every author is credited and no images
          are distributed with this app.</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link target="_blank" href="https://github.com/andybluenoes" class="text-rf-orange">
            andybluenoes
          </b-link>
          <span> - providing feedback and settings research</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link target="_blank" href="https://reshade.me" class="text-rf-orange">
            ReShade
          </b-link>
          <span> - Copyright 2014 Patrick Mours. All rights reserved.</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link target="_blank" href="https://vrtoolkit.retrolux.de" class="text-rf-orange">
            VRToolkit
          </b-link>
          <span> - Copyright (c) 2021, Alexandre Miguel Maia. All rights reserved.</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link target="_blank" href="https://github.com/CXWorld/CapFrameX/releases/latest" class="text-rf-orange">
            CapFrameX
          </b-link>
          <span> - use this to further analyse benchmark capture data!</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link target="_blank" href="https://github.com/GameTechDev/PresentMon" class="text-rf-orange">
            PresentMon
          </b-link>
          <span> - PresentMon is a tool to capture and analyze ETW events related to swap chain presentation on Windows.</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link target="_blank" href="https://github.com/fholger/openvr_fsr#modified-openvr-dll-with-amd-fidelityfx-superresolution--nvidia-image-scaling" class="text-rf-orange">
            OpenVR FSR
          </b-link>
          <span> - Add Image Upscaling via AMD FidelityFX SuperResolution or NVIDIA Image Scaling to SteamVR games.</span>
        </b-list-group-item>
        <b-list-group-item class="bg-dark text-white">
          <b-link target="_blank" href="https://github.com/fholger/openvr_foveated#fixed-foveated-rendering-mod-for-steamvr-games" class="text-rf-orange">
            OpenVR Foveated
          </b-link>
          <span> - Fixed Foveated Rendering for SteamVR games.</span>
        </b-list-group-item>
      </b-list-group>
      <h4 class="mt-5">ReShade - Copyright 2014 Patrick Mours. All rights reserved.</h4>
      <pre class="text-muted">
        BSD-3-Clause License

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
        EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
        OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
        SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
        INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
        TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
        BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
        CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
        ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
        SUCH DAMAGE.
      </pre>
      <h4 class="mt-5">VRToolkit - Copyright (c) 2021, Alexandre Miguel Maia. All rights reserved.</h4>
      <pre class="text-muted">
        BSD 3-Clause License

        Copyright (c) 2021, Alexandre Miguel Maia
        All rights reserved.

        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice, this
           list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright notice,
           this list of conditions and the following disclaimer in the documentation
           and/or other materials provided with the distribution.

        3. Neither the name of the copyright holder nor the names of its
           contributors may be used to endorse or promote products derived from
           this software without specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
        IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
        FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
        DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
        SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
        OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
      </pre>
      <h4 class="mt-5">PresentMon - Copyright (C) 2017-2021 Intel Corporation</h4>
      <pre class="text-muted">
        MIT License
        Permission is hereby granted, free of charge, to any person obtaining a copy of
        this software and associated documentation files (the "Software"), to deal in
        the Software without restriction, including without limitation the rights to
        use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
        of the Software, and to permit persons to whom the Software is furnished to do
        so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
      </pre>
      <h4 class="mt-5">openvr_fsr, openvr_foveated - Copyright (C) 2021, 2022 Holger Frydrych</h4>
      <pre class="text-muted">
        OPENVR LICENSE (BSD 3 clause)
        =============================
        (applies to everything except src/fsr/ffx_a.h and src/fsr/ffx_fsr1.h)

        Copyright (c) 2015, Valve Corporation
        All rights reserved.

        Redistribution and use in source and binary forms, with or without modification,
        are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice, this
        list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright notice,
        this list of conditions and the following disclaimer in the documentation and/or
        other materials provided with the distribution.

        3. Neither the name of the copyright holder nor the names of its contributors
        may be used to endorse or promote products derived from this software without
        specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
        ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
        WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
        ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
        (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
        LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
        ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

        AMD FIDELITYFX SUPERRESOLUTION LICENSE (MIT)
        ============================================
        (applies to src/fsr/ffx_a.h and src/fsr/ffx_fsr1.h)

        Copyright (c) 2021 Advanced Micro Devices, Inc. All rights reserved.

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in
        all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
        THE SOFTWARE.

        NVIDIA IMAGE SCALING LICENSE (MIT)
        ==================================
        (applies to all files in src/nis)

        Copyright(c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

        Permission is hereby granted, free of charge, to any person obtaining a copy of
        this software and associated documentation files(the "Software"), to deal in
        the Software without restriction, including without limitation the rights to
        use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies of
        the Software, and to permit persons to whom the Software is furnished to do so,
        subject to the following conditions :

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
        FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS OR
        COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
        IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
        CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


        NVIDIA NVAPI PUBLIC HEADER (MIT)
        ================================
        (applies to src/nvapi/nvapi.h)

        Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.

        Permission is hereby granted, free of charge, to any person obtaining a
        copy of this software and associated documentation files (the "Software"),
        to deal in the Software without restriction, including without limitation
        the rights to use, copy, modify, merge, publish, distribute, sublicense,
        and/or sell copies of the Software, and to permit persons to whom the
        Software is furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in
        all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
        THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
        FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
        DEALINGS IN THE SOFTWARE.


        Microsoft DirectXTex Screengrab (MIT)
        =====================================
        (applies to src/postprocess/screengrab.{h,cpp})

        Copyright (c) 2011-2021 Microsoft Corp

        Permission is hereby granted, free of charge, to any person obtaining a copy of this
        software and associated documentation files (the "Software"), to deal in the Software
        without restriction, including without limitation the rights to use, copy, modify,
        merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
        permit persons to whom the Software is furnished to do so, subject to the following
        conditions:

        The above copyright notice and this permission notice shall be included in all copies
        or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
        INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
        PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
        HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
        CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
        OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
      </pre>
    </b-card>

    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">Danger Zone</span></h6>
      </template>
      <b-button variant="primary" @click="$emit('nav', 8)">Show App Logs</b-button>
      <b-button class="ml-2" variant="danger" @click="testException">Produce Test App Exception</b-button>
      <p></p>
      <b-button-group size="sm">
        <b-button @click="playAudio('audioConfirm')">audioConfirm</b-button>
        <b-button @click="playAudio('audioPing')">audioPing</b-button>
        <b-button @click="playAudio('audioIndicator')">audioIndicator</b-button>
        <b-button @click="playAudio('audioSelect')">audioSelect</b-button>
        <b-button @click="playAudio('audioCuteSelect')">audioCuteSelect</b-button>
      </b-button-group>
      <b-button-group size="sm">
        <b-button @click="playAudio('audioSwitch')">audioSwitch</b-button>
        <b-button @click="playAudio('audioSwitchOn')">audioSwitchOn</b-button>
        <b-button @click="playAudio('audioSwitchOff')">audioSwitchOff</b-button>
        <b-button @click="playAudio('audioFlash')">audioFlash</b-button>
      </b-button-group>
    </b-card>
  </div>
</template>

<script>

import {version} from "../../package.json";

export default {
  name: "AppWiki",
  data: function () {
    return {
      ver: version,
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    testException: async function () { await window.eel.test_app_exception() },
    playAudio: async function (audioEffectName) { this.$eventHub.$emit('play-audio', audioEffectName) },
  },
  components: {
  },
}
</script>

<style scoped>
h1, h2, h3, h4, h5 { font-family: Inter, "Segoe UI", system-ui, sans-serif; }
.spacer { width: 100%; height: 1.75rem; background: #efefef; }
</style>

<style>

</style>