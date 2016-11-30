/*
 * Copyright (c) 2016 Adrien Lecharpentier
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

package fr.alecharp.simpleapp;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author Adrien Lecharpentier
 */
@RestController
public final class GravatarHttpController {
    private static final String GRAVATAR_URL = "https://secure.gravatar.com/avatar/";
    private static final Logger LOG = LoggerFactory.getLogger(GravatarHttpController.class);
    private final HashService hashService;

    @Autowired
    public GravatarHttpController(HashService hashService) {
        this.hashService = hashService;
    }

    @RequestMapping(value = "/api/img")
    public String getImage(@RequestParam(required = false) String email,
                           @RequestParam(defaultValue = "450", required = false) String size) {
        LOG.debug("Fetch image for {} in {}", email, size);
        return String.format("%s%s?s=%s&r=g", GRAVATAR_URL, hashService.md5(email), size);
    }
}
